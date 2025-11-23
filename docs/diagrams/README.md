# Workflow Diagrams

This directory contains all workflow and architecture diagrams for the Travel Buddy project.

## Diagrams

1. **System Architecture** (`system-architecture.mmd`)
   - Complete system architecture showing all layers and components
   - Includes UI, Authentication, Orchestration, Agents, and Infrastructure

2. **Workflow Sequence** (`workflow-sequence.mmd`)
   - Detailed sequence diagram showing the complete workflow
   - Shows interaction between all agents and the orchestrator
   - Includes logging and state management

3. **Workflow State Flow** (`workflow-state-flow.mmd`)
   - Flowchart showing state transitions through the workflow
   - Visual representation of agent execution order
   - Shows state updates at each phase

4. **Agent Execution Flow** (`agent-execution-flow.mmd`)
   - Error handling and retry logic flow
   - Shows how agents handle API calls and errors
   - Exponential backoff mechanism

5. **Authentication & Data Flow** (`authentication-data-flow.mmd`)
   - User authentication sequence
   - Chat history management
   - Database interactions

## Viewing Diagrams

These diagrams are in Mermaid format (`.mmd`). You can view them:

1. **GitHub**: GitHub automatically renders Mermaid diagrams in markdown files
2. **VS Code**: Install the "Markdown Preview Mermaid Support" extension
3. **Online**: Use [Mermaid Live Editor](https://mermaid.live/)
4. **CLI**: Use [Mermaid CLI](https://github.com/mermaid-js/mermaid-cli) to generate images

## Generating Images

To convert these diagrams to images (PNG/SVG):

```bash
# Install Mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# Generate PNG images
mmdc -i system-architecture.mmd -o system-architecture.png
mmdc -i workflow-sequence.mmd -o workflow-sequence.png
mmdc -i workflow-state-flow.mmd -o workflow-state-flow.png
mmdc -i agent-execution-flow.mmd -o agent-execution-flow.png
mmdc -i authentication-data-flow.mmd -o authentication-data-flow.png
```

## Updating Diagrams

When updating diagrams:
1. Edit the `.mmd` files directly
2. Test the syntax using Mermaid Live Editor
3. Update the README.md references if diagram names change
4. Regenerate images if using image format

