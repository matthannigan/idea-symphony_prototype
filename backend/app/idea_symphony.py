from typing import List, Dict, Any
from pydantic_ai import Agent, format_as_xml
from shared.models import (
    IdeaInput, BrainstormingContext, BrainstormQuestions,
    BrainstormResponse, BrainstormSynthesis
)

class IdeaSymphony:
    def __init__(self):
        # Store only agent configurations, not Agent instances
        self.context_agent_config = {
            "model": 'google-gla:gemini-2.5-flash-preview-04-17',
            "output_type": BrainstormingContext,
            "system_prompt": "You are an expert at distilling information into clear, concise context documents."
        }
        self.question_generator_agent_config = {
            "model": 'google-gla:gemini-2.5-flash-preview-04-17',
            "output_type": BrainstormQuestions,
            "system_prompt": """
            You are an expert facilitator who generates thoughtful brainstorming questions.
            Review the attached information and create brainstorming questions to further develop the project.
            Group similar questions under relevant headings.
            For each question, provide a short summary and a more detailed description.
            """
        }
        self.question_synthesizer_agent_config = {
            "model": 'google-gla:gemini-2.5-flash-preview-04-17',
            "output_type": BrainstormQuestions,
            "system_prompt": """
            You are an expert facilitator who synthesizes brainstorming questions.
            Take multiple sets of questions and synthesize them into a single comprehensive list.
            Eliminate duplication and group similar questions under relevant headings.
            Preserve the format of short summary and detailed description for each question.
            """
        }
        self.brainstorming_agent_config = {
            "model": 'google-gla:gemini-2.5-flash-preview-04-17',
            "output_type": List[BrainstormResponse],
            "system_prompt": """
            Act as a coach who assists the user in refining their plan.
            You will receive a project overview and a set of clarifying questions.
            For each question, provide 3-5 unique detailed responses.
            Make your responses specific, actionable, and insightful.
            """
        }
        self.synthesis_agent_config = {
            "model": 'google-gla:gemini-2.5-flash-preview-04-17',
            "output_type": BrainstormSynthesis,
            "system_prompt": """
            You are an expert facilitator who synthesizes brainstorming session outputs.
            Take multiple participant responses and synthesize them into a cohesive document.
            Aggregate similar ideas while preserving unique insights.
            Create both an attributed version (showing which participant generated which idea)
            and a clean, non-attributed version for a more streamlined reading experience.
            """
        }

    async def create_context(self, idea_input: IdeaInput) -> BrainstormingContext:
        """Generate a distilled context document from the user's input"""
        prompt = format_as_xml({
            "idea": idea_input.idea_text,
            "document": idea_input.document_content or "No additional document provided"
        })
        agent = Agent(**self.context_agent_config)
        result = await agent.run(
            f"Please distill the following information into a clear, concise context document for brainstorming: {prompt}"
        )
        return result.output

    async def generate_questions(self, context: BrainstormingContext, model_count: int = 1) -> List[BrainstormQuestions]:
        """Generate questions from multiple models"""
        question_sets = []
        for i in range(model_count):
            agent = Agent(**self.question_generator_agent_config)
            result = await agent.run(
                f"Review this project information and generate {5+i*2}-{8+i*3} brainstorming questions to help develop it further: {context.context}"
            )
            question_sets.append(result.output)
        return question_sets

    async def synthesize_questions(self, question_sets: List[BrainstormQuestions]) -> BrainstormQuestions:
        """Synthesize multiple sets of questions into one cohesive set"""
        if len(question_sets) == 1:
            return question_sets[0]
        formatted_sets = [format_as_xml(qs) for qs in question_sets]
        combined = "\n\n".join([f"Question Set {i+1}:\n{set_text}" for i, set_text in enumerate(formatted_sets)])
        agent = Agent(**self.question_synthesizer_agent_config)
        result = await agent.run(
            f"Synthesize these sets of questions into a single comprehensive list, eliminating duplication: {combined}"
        )
        return result.output

    async def chunk_questions(self, questions: BrainstormQuestions) -> List[Dict[str, Any]]:
        """Group questions by topic area for more efficient processing"""
        chunks = []
        for group in questions.question_groups:
            chunk = {
                "heading": group.heading,
                "questions": []
            }
            for question in group.questions:
                chunk["questions"].append({
                    "short_summary": question.short_summary,
                    "full_description": question.full_description
                })
            chunks.append(chunk)
        return chunks

    async def brainstorm_responses(
        self, 
        context: BrainstormingContext, 
        question_chunks: List[Dict[str, Any]], 
        participant_count: int = 2
    ) -> List[List[BrainstormResponse]]:
        """Generate brainstorming responses from multiple participants"""
        all_participant_responses = []
        for participant in range(participant_count):
            participant_responses = []
            for chunk in question_chunks:
                prompt = format_as_xml({
                    "context": context.context,
                    "topic": chunk["heading"],
                    "questions": chunk["questions"]
                })
                agent = Agent(**self.brainstorming_agent_config)
                result = await agent.run(
                    f"You are Participant {participant + 1}. Please answer the following brainstorming questions "
                    f"for this project. For each question, provide 3-5 unique responses:\n\n{prompt}"
                )
                participant_responses.extend(result.output)
            all_participant_responses.append(participant_responses)
        return all_participant_responses

    async def synthesize_responses(self, all_responses: List[List[BrainstormResponse]]) -> BrainstormSynthesis:
        """Synthesize all brainstorming responses into a final document"""
        formatted_responses = []
        for i, participant_responses in enumerate(all_responses):
            participant_text = f"## Participant {i+1} Responses\n\n"
            for response in participant_responses:
                participant_text += f"### {response.question}\n\n"
                for j, answer in enumerate(response.answers):
                    participant_text += f"- {answer}\n"
                participant_text += "\n"
            formatted_responses.append(participant_text)
        combined_responses = "\n\n".join(formatted_responses)
        agent = Agent(**self.synthesis_agent_config)
        result = await agent.run(
            f"Synthesize these brainstorming responses into a cohesive document that preserves unique insights "
            f"while aggregating similar ideas:\n\n{combined_responses}"
        )
        return result.output
