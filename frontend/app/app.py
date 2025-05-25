import streamlit as st
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
import httpx
from client import IdeaSymphonyClient
import json, os
from shared.models import (
    IdeaInput, BrainstormingContext, BrainstormQuestions,
    BrainstormResponse, BrainstormSynthesis
)

# Helper to run async functions in Streamlit
def run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

def initialize_session_state():
    """Initialize all session state variables"""
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'use_mock_data' not in st.session_state:
        st.session_state.use_mock_data = False
    if 'client' not in st.session_state:
        st.session_state.client = IdeaSymphonyClient(use_mock_data=st.session_state.use_mock_data)
    if 'idea_input' not in st.session_state:
        st.session_state.idea_input = None
    if 'context' not in st.session_state:
        st.session_state.context = None
    if 'question_sets' not in st.session_state:
        st.session_state.question_sets = None
    if 'synthesized_questions' not in st.session_state:
        st.session_state.synthesized_questions = None
    if 'question_chunks' not in st.session_state:
        st.session_state.question_chunks = None
    if 'all_responses' not in st.session_state:
        st.session_state.all_responses = None
    if 'final_synthesis' not in st.session_state:
        st.session_state.final_synthesis = None
    if 'error' not in st.session_state:
        st.session_state.error = None

def handle_error(error: Exception):
    """Handle and display errors"""
    st.session_state.error = str(error)
    st.error(f"An error occurred: {error}")

def main():
    st.set_page_config(page_title="Idea Symphony", page_icon="🎵", layout="wide")
    st.title("💡 Idea Symphony 🎵")
    st.subheader("AI-Powered Brainstorming")
    
    # Initialize session state first
    initialize_session_state()
    
    # Add mock data toggle in the sidebar
    with st.sidebar:
        st.markdown("### Development Settings")
        use_mock_data = st.toggle(
            "Use Mock Data",
            value=st.session_state.use_mock_data,
            help="Toggle to use mock data instead of making API calls"
        )
        
        # Update client if mock data setting changed
        if use_mock_data != st.session_state.use_mock_data:
            st.session_state.use_mock_data = use_mock_data
            st.session_state.client = IdeaSymphonyClient(use_mock_data=use_mock_data)
            # Clear any existing data when switching modes
            for key in ['context', 'question_sets', 'synthesized_questions', 
                       'question_chunks', 'all_responses', 'final_synthesis']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    # Display any errors
    if st.session_state.error:
        st.error(st.session_state.error)
        if st.button("Clear Error"):
            st.session_state.error = None
            st.rerun()
    
    # Step 1: Initial Input and Upload
    if st.session_state.step == 1:
        st.markdown("### Step 1: Share Your Idea")
        
        with st.form("idea_form"):
            idea_text = st.text_area("I have an idea for...", height=150)
            uploaded_file = st.file_uploader("Upload supporting document (optional)", type=["txt", "md"])
            submit_button = st.form_submit_button("Start Brainstorming")
            
            if submit_button:
                document_content = None
                if uploaded_file is not None:
                    document_content = uploaded_file.read().decode("utf-8")
                # If using mock data, override idea_text and ignore uploaded file
                if st.session_state.use_mock_data:
                    mock_data_path = os.path.join(os.path.dirname(__file__), "mock_data.json")
                    with open(mock_data_path, "r") as f:
                        mock_data = json.load(f)
                    idea_text = mock_data.get("idea_text")
                    document_content = None
                st.session_state.idea_input = {
                    "idea_text": idea_text,
                    "document_content": document_content
                }
                st.session_state.step = 2
                st.rerun()
    
    # Step 2: Create Brainstorming Context Document
    elif st.session_state.step == 2:
        st.markdown("### Step 2: Create Brainstorming Context")
        
        # Display the user's input
        st.markdown("#### Your Idea:")
        st.markdown(st.session_state.idea_input["idea_text"])
        
        if st.session_state.idea_input["document_content"]:
            with st.expander("View Uploaded Document"):
                st.markdown(st.session_state.idea_input["document_content"])
        
        # Create context document if not already done
        if st.session_state.context is None:
            with st.spinner("Creating context document..."):
                try:
                    st.session_state.context = run_async(
                        st.session_state.client.create_context(
                            st.session_state.idea_input["idea_text"],
                            st.session_state.idea_input["document_content"]
                        )
                    )
                except Exception as e:
                    handle_error(e)
                    return
        
        # Display the context document
        st.markdown("#### Brainstorming Context:")
        context_text = st.text_area(
            "Review and edit the context if needed:",
            value=st.session_state.context["context"],
            height=300
        )
        
        # Update context if edited
        if context_text != st.session_state.context["context"]:
            st.session_state.context["context"] = context_text
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back to Idea"):
                st.session_state.step = 1
                st.rerun()
        
        with col2:
            if st.button("Configure Brainstorming ➡️"):
                st.session_state.step = 3
                st.rerun()
    
    # Step 3: Configure Brainstorming Session
    elif st.session_state.step == 3:
        st.markdown("### Step 3: Configure Brainstorming Session")
        
        # Display the context
        with st.expander("View Brainstorming Context"):
            st.markdown(st.session_state.context["context"])
        
        # Settings for brainstorming
        st.markdown("#### Brainstorming Settings:")
        
        # Question generation settings
        st.markdown("##### Question Generation")
        model_count = st.slider(
            "Number of question-generating models to use:",
            1, 3, 1,
            key="model_count_slider"
        )
        
        # Participant settings
        st.markdown("##### Brainstorming Participants")
        participant_count = st.slider(
            "Number of AI brainstorming participants:",
            2, 5, 2
        )
        
        # Human participation option
        include_human = st.checkbox("I want to participate in the brainstorming")
        
        # Display estimated processing time
        st.info(f"Estimated processing time: {participant_count * 2}-{participant_count * 5} minutes")
        
        # Store settings in session state
        if 'model_count' not in st.session_state or st.session_state.model_count != model_count:
            st.session_state.model_count = model_count
            st.session_state.question_sets = None
        
        st.session_state.participant_count = participant_count
        st.session_state.include_human = include_human
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back to Context"):
                st.session_state.step = 2
                st.rerun()
        
        with col2:
            if st.button("Generate Questions ➡️"):
                st.session_state.step = 4
                st.rerun()
    
    # Step 4: Generate Brainstorming Questions
    elif st.session_state.step == 4:
        st.markdown("### Step 4: Generate Brainstorming Questions")
        
        # Display the context
        with st.expander("View Brainstorming Context"):
            st.markdown(st.session_state.context["context"])
        
        # Generate questions if not already done
        if st.session_state.question_sets is None:
            with st.spinner(f"Generating questions using {st.session_state.model_count} model{'s' if st.session_state.model_count > 1 else ''}..."):
                try:
                    context_model = BrainstormingContext(**st.session_state.context)
                    st.session_state.question_sets = run_async(
                        st.session_state.client.generate_questions(
                            context_model,
                            st.session_state.model_count
                        )
                    )
                except Exception as e:
                    handle_error(e)
                    return
        
        # If only one model, pre-chunk questions for later steps
        if st.session_state.model_count == 1:
            synthesized_model = BrainstormQuestions(**st.session_state.synthesized_questions)
            st.session_state.question_chunks = run_async(
                st.session_state.client.chunk_questions(synthesized_model)
            )
        
        # Display question sets
        if st.session_state.question_sets is not None:
            if len(st.session_state.question_sets) > 1:
                st.markdown("#### Generated Question Sets:")
                tabs = st.tabs([f"Question Set {i+1}" for i in range(len(st.session_state.question_sets))])
                
                for i, tab in enumerate(tabs):
                    with tab:
                        question_set = st.session_state.question_sets[i]
                        for group in question_set["question_groups"]:
                            st.markdown(f"#### {group['heading']}")
                            for q in group["questions"]:
                                st.markdown(f"**{q['short_summary']}**: {q['full_description']}")
            else:
                st.markdown("#### Generated Questions:")
                question_set = st.session_state.question_sets[0]
                for group in question_set["question_groups"]:
                    st.markdown(f"#### {group['heading']}")
                    for q in group["questions"]:
                        st.markdown(f"**{q['short_summary']}**: {q['full_description']}")
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back to Configuration"):
                st.session_state.step = 3
                st.rerun()
        
        with col2:
            button_text = "Synthesize Questions ➡️" if st.session_state.model_count != 1 else "Start Brainstorming ➡️"
            if st.button(button_text):
                if st.session_state.model_count == 1:
                    if st.session_state.include_human:
                        st.session_state.step = 6
                    else:
                        st.session_state.step = 7
                else:
                    st.session_state.step = 5
                st.rerun()
    
    # Step 5: Synthesize Questions
    elif st.session_state.step == 5:
        st.markdown("### Step 5: Synthesize Questions")
        
        # Display the context
        with st.expander("View Brainstorming Context"):
            st.markdown(st.session_state.context["context"])
        
        # Synthesize questions if not already done
        if st.session_state.synthesized_questions is None:
            with st.spinner("Synthesizing questions..."):
                try:
                    question_set_models = [BrainstormQuestions(**qs) for qs in st.session_state.question_sets]
                    st.session_state.synthesized_questions = run_async(
                        st.session_state.client.synthesize_questions(question_set_models)
                    )
                    synthesized_model = BrainstormQuestions(**st.session_state.synthesized_questions)
                    st.session_state.question_chunks = run_async(
                        st.session_state.client.chunk_questions(synthesized_model)
                    )
                except Exception as e:
                    handle_error(e)
                    return
        
        # Display synthesized questions
        st.markdown("#### Synthesized Questions:")
        synthesized = st.session_state.synthesized_questions
        for group in synthesized["question_groups"]:
            st.markdown(f"#### {group['heading']}")
            for q in group["questions"]:
                st.markdown(f"**{q['short_summary']}**: {q['full_description']}")
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back to Question Generation"):
                st.session_state.synthesized_questions = None
                st.session_state.question_chunks = None
                st.session_state.step = 4
                st.rerun()
        
        with col2:
            if st.button("Start Brainstorming ➡️"):
                if st.session_state.include_human:
                    st.session_state.step = 6
                else:
                    st.session_state.step = 7
                st.rerun()
    
    # Step 6: Human Participation (optional)
    elif st.session_state.step == 6:
        st.markdown("### Step 6: Human Participation")
        
        # Display the context
        with st.expander("View Brainstorming Context"):
            st.markdown(st.session_state.context["context"])
        
        # Initialize human responses if not existing
        if 'human_responses' not in st.session_state:
            st.session_state.human_responses = []
            for chunk in st.session_state.question_chunks:
                for question in chunk["questions"]:
                    st.session_state.human_responses.append({
                        "question": question["short_summary"],
                        "answers": [""]
                    })
        
        # Display questions for human to answer
        st.markdown("#### Answer the brainstorming questions:")
        st.markdown("Provide your own responses to the questions below. You can add multiple responses to each question.")
        
        updated_responses = []
        
        for i, chunk in enumerate(st.session_state.question_chunks):
            st.markdown(f"### {chunk['heading']}")
            
            for j, question in enumerate(chunk["questions"]):
                st.markdown(f"**{question['short_summary']}**: {question['full_description']}")
                
                # Find matching response
                response_index = next(
                    (idx for idx, r in enumerate(st.session_state.human_responses)
                     if r["question"] == question["short_summary"]),
                    None
                )
                
                if response_index is not None:
                    current_answers = st.session_state.human_responses[response_index]["answers"]
                    
                    # Display text areas for each answer
                    new_answers = []
                    for k, answer in enumerate(current_answers):
                        new_answer = st.text_area(
                            f"Response {k+1}",
                            value=answer,
                            key=f"human_answer_{i}_{j}_{k}"
                        )
                        new_answers.append(new_answer)
                    
                    # Add button to add another response
                    if st.button("+ Add another response", key=f"add_response_{i}_{j}"):
                        new_answers.append("")
                    
                    # Store updated answers
                    updated_response = {
                        "question": question["short_summary"],
                        "answers": [a for a in new_answers if a.strip()]
                    }
                    updated_responses.append(updated_response)
                
                st.markdown("---")
        
        # Update human responses
        if updated_responses:
            st.session_state.human_responses = updated_responses
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back to Participant Selection"):
                if 'human_responses' in st.session_state:
                    del st.session_state.human_responses
                st.session_state.step = 5
                st.rerun()
        
        with col2:
            if st.button("Continue to AI Brainstorming ➡️"):
                # Convert human responses to the expected format
                human_brainstorm_responses = [
                    {
                        "question": response["question"],
                        "answers": [a for a in response["answers"] if a.strip()]
                    }
                    for response in st.session_state.human_responses
                    if response["answers"] and any(a.strip() for a in response["answers"])
                ]
                
                st.session_state.human_brainstorm_responses = human_brainstorm_responses
                st.session_state.step = 7
                st.rerun()
    
    # Step 7: Run AI Brainstorming
    elif st.session_state.step == 7:
        st.markdown("### Step 7: AI Brainstorming")
        
        # Generate AI responses if not already done
        if st.session_state.all_responses is None:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                with st.spinner("Generating AI responses..."):
                    context_model = BrainstormingContext(**st.session_state.context)
                    st.session_state.all_responses = run_async(
                        st.session_state.client.brainstorm(
                            context_model,
                            st.session_state.question_chunks,
                            st.session_state.participant_count
                        )
                    )
                    
                    # Add human responses if included
                    if st.session_state.include_human and hasattr(st.session_state, 'human_brainstorm_responses'):
                        st.session_state.all_responses.append(st.session_state.human_brainstorm_responses)
                
                status_text.success("All responses generated!")
            except Exception as e:
                handle_error(e)
                return
        
        # Display responses
        st.markdown("#### Brainstorming Responses:")
        
        try:
            participant_tabs = st.tabs([
                f"Participant {i+1}" for i in range(len(st.session_state.all_responses))
            ])
            
            for i, tab in enumerate(participant_tabs):
                with tab:
                    participant_responses = st.session_state.all_responses[i]
                    current_topic = None
                    
                    for response in participant_responses:
                        question = response.get("question")
                        answers = response.get("answers", [])
                        
                        # Find topic for this question
                        topic = None
                        for chunk in st.session_state.question_chunks:
                            for question_obj in chunk["questions"]:
                                if question_obj["short_summary"] == question:
                                    topic = chunk["heading"]
                                    break
                            if topic:
                                break
                        
                        # Display topic if changed
                        if topic and topic != current_topic:
                            st.markdown(f"### {topic}")
                            current_topic = topic
                        
                        st.markdown(f"#### {question}")
                        for answer in answers:
                            st.markdown(f"- {answer}")
        except Exception as e:
            handle_error(e)
            return
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back to Previous Step"):
                st.session_state.all_responses = None
                if st.session_state.include_human:
                    st.session_state.step = 6
                else:
                    st.session_state.step = 5
                st.rerun()
        
        with col2:
            if st.button("Synthesize Results ➡️"):
                st.session_state.step = 8
                st.rerun()
    
    # Step 8: Synthesize Results
    elif st.session_state.step == 8:
        st.markdown("### Step 8: Synthesize Results")
        
        # Synthesize results if not already done
        if st.session_state.final_synthesis is None:
            with st.spinner("Synthesizing all brainstorming responses..."):
                try:
                    all_responses_models = [
                        [BrainstormResponse(**resp) for resp in participant]
                        for participant in st.session_state.all_responses
                    ]
                    st.session_state.final_synthesis = run_async(
                        st.session_state.client.synthesize(all_responses_models)
                    )
                except Exception as e:
                    handle_error(e)
                    return
        
        # Display the final synthesis
        st.markdown("#### Final Synthesis:")
        
        tabs = st.tabs(["Non-Attributed Version", "Attributed Version"])
        
        with tabs[0]:
            st.markdown(st.session_state.final_synthesis["synthesized_content"])
            
            # Download button for non-attributed version
            non_attributed_md = st.session_state.final_synthesis["synthesized_content"]
            st.download_button(
                label="Download Non-Attributed Version (Markdown)",
                data=non_attributed_md,
                file_name=f"IdeaSymphony_Synthesis_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown"
            )
        
        with tabs[1]:
            if st.session_state.final_synthesis.get("attributed_content"):
                st.markdown(st.session_state.final_synthesis["attributed_content"])
                
                # Download button for attributed version
                attributed_md = st.session_state.final_synthesis["attributed_content"]
                st.download_button(
                    label="Download Attributed Version (Markdown)",
                    data=attributed_md,
                    file_name=f"IdeaSymphony_Synthesis_Attributed_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                    mime="text/markdown"
                )
            else:
                st.info("Attributed version not available for this synthesis.")
        
        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back to Brainstorming"):
                st.session_state.final_synthesis = None
                st.session_state.step = 7
                st.rerun()
        
        with col2:
            if st.button("Start New Brainstorming Session"):
                # Clear all session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

if __name__ == "__main__":
    main()
