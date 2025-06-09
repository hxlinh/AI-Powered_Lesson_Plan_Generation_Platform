# AI-Powered Lesson Plan Generation Platform using fine-tuned AI and RAG

## Overview
<img width="1156" alt="web interface" src="https://github.com/user-attachments/assets/71ed837d-195a-43b6-bfa9-321bcd68105e" />

This project is an innovative web platform that leverages generative Artificial Intelligence (AI) to significantly assist instructors in creating lesson plans efficiently. Developed as part of an AI competition, the system automates the generation of teaching content, including Course Learning Outcomes (CLOs) and Course Syllabus (CS), based on input materials and pedagogical standards. Furthermore, the platform integrates an advanced AI-powered Retrieval-Augmented Generation (RAG) system to enable instructors to retrieve information and answer questions directly from specific lesson materials during teaching sessions, thereby streamlining preparation and enhancing teaching quality.

The platform integrates cutting-edge technologies such as fine-tuned Large Language Models (LLMs), RAG, Optical Character Recognition (OCR), and a self-improving mechanism, all delivered through a full-stack web application.

## Features

- **Automated CLOs & CS Generation:** Quickly generates structured Course Learning Outcomes (CLOs) and Course Syllabi based on course information, PLOs, and uploaded teaching materials, adhering to pedagogical principles like Bloom's Taxonomy and SMART criteria.
- **Contextual Q&A with RAG:** Allows instructors to ask questions related to specific lesson content, with the AI providing precise answers by retrieving information directly from the uploaded teaching documents.
- **Document Content Extraction (OCR & CNN):** Processes PDF teaching materials, extracting and categorizing content (text, images, tables) for AI processing and RAG.
- **Instructor Feedback Loop (Self-Improving):** The system incorporates a mechanism to adjust and refine AI outputs based on instructor feedback, continuously improving the quality of generated content.
- **Intuitive Web Interface:** A user-friendly ReactJS frontend facilitates seamless interaction for course creation, content confirmation, CLOs/CS adjustments via chatbot, and lesson plan utilization.
- **Flexible Data Management:** Backend operations manage course data and AI interactions via a Python (Flask) API and JSON file-based storage.

## Demo

Check out the video demonstration of the app here: [Video Demo](https://drive.google.com/file/d/1MEsqfNTqbhqYnghlhjt3hzBjzc0jCMvo/view?usp=sharing).

## How It Works
The platform operates through a sophisticated integration of AI and web technologies:
1. **Course Creation & Document Ingestion:**
- Instructors input course details (subject, number of lessons, duration) and upload teaching materials (PDFs) via the ReactJS frontend.
- The backend (Flask) processes the PDF using **OCR** (via libraries like Unstructured) to extract and categorize content (text, tables, images). Instructors confirm the extracted content via a table of contents.
2. **LLM Fine-tuning & Content Generation:**
- **A fine-tuned LLaMa 3.1-8B model** (leveraging **Unsloth** for efficient training) is central to generating CLOs and CS. This model is specifically trained on pedagogical guidelines (Bloom's Taxonomy, SMART principles) and examples of standard course structures.
- The LLM generates initial CLOs and CS, which instructors can then refine through an interactive chatbot interface.
3. **Retrieval-Augmented Generation (RAG) for Contextual Q&A:**
- For the RAG system, extracted document content is summarized (e.g., using a GPT model) and converted into numerical embeddings (*OpenAIEmbeddings* from *langchain.embeddings*). These embeddings are stored in a **ChromaDB** vector database, while the original content is kept in a document store.
- When an instructor asks a question related to a specific lesson, the system queries *ChromaDB* to find relevant content chunks. These retrieved original content pieces, along with the instructor's query, are then fed to the LLM to generate highly contextual and accurate answers, ensuring responses are grounded in the provided teaching materials.
4. **Backend & Frontend Interaction:**
- **The Python (Flask) backend** serves as the central hub, exposing RESTful APIs for all functionalities: course management (create, update, delete), PDF processing, LLM interaction (for CLOs/CS generation and RAG queries), and chat functionalities.
- Data is persistently stored and managed using **JSON files** on the backend, providing a flexible NoSQL-like database approach.
- The **ReactJS frontend** provides an intuitive user experience, handling user inputs, displaying generated content, managing chat interactions, and presenting a side-by-side PDF viewer for reference during content generation and Q&A sessions.
5. **Self-Improving Mechanism:**