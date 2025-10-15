# Inventory Management System - Frontend

A modern, TypeScript-based React frontend for the inventory management system.

## Tech Stack

- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **React Router v7** - Client-side routing
- **TanStack React Query** - Server state management and caching
- **Axios** - HTTP client
- **Tailwind CSS** - Utility-first styling
- **React Hook Form** - Form handling
- **Zod** - Schema validation
- **date-fns** - Date formatting

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:5000`

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at `http://localhost:3000`

### Build for Production

```bash
# Build optimized production bundle
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
src/
├── api/              # API client and endpoint functions
│   ├── client.ts     # Axios instance and interceptors
│   ├── inventory.ts  # Inventory API functions
│   ├── checkout.ts   # Checkout API functions
│   └── index.ts      # Export all API functions
├── components/       # Reusable components
│   ├── ui/          # Base UI components (Button, Card, Badge, etc.)
│   ├── layout/      # Layout components (Navbar, Layout)
│   └── features/    # Feature-specific components (ItemCard)
├── context/         # React Context providers
│   └── AppContext.tsx  # Global app state
├── pages/           # Page components
│   ├── DashboardPage.tsx
│   ├── InventoryPage.tsx
│   ├── ItemDetailsPage.tsx
│   ├── CheckoutsPage.tsx
│   └── OverduePage.tsx
├── types/           # TypeScript type definitions
│   └── index.ts     # All TypeScript interfaces
├── App.tsx          # Main app component with routing
├── main.tsx         # Application entry point
└── index.css        # Global styles with Tailwind
```

## Features

### Implemented

- **Dashboard** - Overview with key metrics and stats
- **Inventory Management**
  - View all items by location
  - Search items by name or category
  - View item details and checkout history
  - Real-time availability status
- **Active Checkouts** - View all currently checked out items
- **Overdue Tracking** - View and manage overdue items
- **Location Selector** - Switch between different locations (San Jose, 3K, 2U)
- **Responsive Design** - Mobile-friendly interface

### To Be Implemented

- **Checkout Form** - Modal for checking out items
- **Check-in Form** - Modal for returning items
- **User Authentication** - Login and user management
- **Advanced Filters** - Category, status, and availability filters
- **Notifications** - Toast notifications for actions
- **User Profile** - View user checkout history

## Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_BASE_URL=http://localhost:5000
```

## API Integration

The frontend communicates with the Flask backend via REST API:

- **Inventory**: `GET /api/inventory`, `GET /api/inventory/search`, `GET /api/inventory/:id`
- **Checkouts**: `POST /api/checkout`, `POST /api/checkout/checkin`
- **Active/Overdue**: `GET /api/checkout/active`, `GET /api/checkout/overdue`
- **History**: `GET /api/checkout/user/:ldap`, `GET /api/checkout/item/:id/history`

## Development

### Key Concepts

- **React Query** - Handles server state, caching, and automatic refetching
- **Context API** - Manages global state (current location, user)
- **TypeScript** - Provides type safety for API responses and props
- **Tailwind CSS** - Utility classes for rapid UI development

### Adding a New Page

1. Create page component in `src/pages/`
2. Add route in `src/App.tsx`
3. Add navigation link in `src/components/layout/Navbar.tsx`

### Adding a New API Endpoint

1. Define TypeScript types in `src/types/index.ts`
2. Create API function in `src/api/`
3. Use with React Query in components

## Troubleshooting

### Dev server not starting
- Ensure port 3000 is not in use
- Check that all dependencies are installed

### API calls failing
- Verify backend is running on `http://localhost:5000`
- Check CORS configuration in backend
- Verify API endpoint URLs in `src/api/`

### Build errors
- Run `npm run lint` to check TypeScript errors
- Ensure all imports are correct
- Check that all required dependencies are installed

## License

ISC