# System Architecture

## Overview
The chatbot system is modular, with clear separation between UI, business logic, and data management.

## Main Components
- **app.py**: Streamlit UI and main app logic
- **components/**: UI components (sidebar, model selector, etc.)
- **services/**: Business logic (LLM service, chat management, analytics)
- **data/**: Chat history storage (JSON files)
- **themes/**: CSS for light/dark themes
- **utils/**: Helper functions
- **tests/**: Unit and integration tests

## Data Flow
1. User interacts with Streamlit UI
2. Messages are processed and sent to the LLM service
3. Responses and metadata are stored in chat history
4. Analytics and search features read from chat history

## Diagram
```
[User] <-> [Streamlit UI (app.py)] <-> [Services] <-> [Data/Chat History]
                                 ^
                                 |
                          [Components]
```

## Security
- API keys are loaded from environment variables
- File uploads are validated
- No sensitive data is stored in code
