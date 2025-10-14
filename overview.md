## Project Overview

This is the **Hierarchical Data Explorer**, a web application for visualizing and managing complex, nested business data using a multi-pane (columnar) layout. The application displays a four-tier hierarchy: Customers → Projects → Quotes → Vendor freight requests.

## Technical Stack
- **Frontend**: HTMX + Alpine.js
- **Data**: Normalized JSON files (mimicking relational database structure)


## Key Implementation Requirements

### Multi-Pane Navigation
- Each pane displays items as cards with relevant information (name, ID, status, child count)
- Selecting an item populates the adjacent pane with filtered child data
- Clearing a selection clears all subsequent panes

### Core Features
- Dynamic sorting controls in each pane

## Development Approach

1. **Backend First**: Set up FastAPI server with JSON data files and API endpoints
2. **Frontend Foundation**: Create basic app with component hierarchy
3. **Data Flow**: Implement reactive data fetching and state management
4. **UI Polish**: Add styling, sorting, editing capabilities

 ## Features:
  - 4-Level Hierarchy Navigation: Customers → Projects → Quotes → Vendor Freight Requests
  - Details Column: Interactive Accordion: Complete hierarchy display with sibling navigation
  - Reactive State Management
  - Data Enrichment: Vendor names integrated with freight requests
  - Card-Based UI: Responsive layout