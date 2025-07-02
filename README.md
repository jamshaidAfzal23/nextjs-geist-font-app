# Smart CRM SaaS - Complete Full-Stack Application

A comprehensive Customer Relationship Management (CRM) system built with modern technologies. This project demonstrates a complete full-stack application with a FastAPI backend and Next.js frontend, featuring authentication, CRUD operations, and a professional UI.

## 🚀 Features

### Backend (FastAPI)
- **RESTful API** with comprehensive endpoints
- **Authentication & Authorization** with JWT tokens
- **Database Management** with SQLAlchemy ORM
- **Data Validation** with Pydantic schemas
- **Role-based Access Control** (RBAC)
- **Comprehensive Documentation** with automatic OpenAPI/Swagger
- **Error Handling** and logging
- **CORS Configuration** for frontend integration

### Frontend (Next.js)
- **Modern React** with Next.js 14 and TypeScript
- **Responsive Design** with Tailwind CSS
- **Authentication Context** with protected routes
- **Type-safe API Integration** with Axios
- **Professional UI Components** with shadcn/ui design system
- **Real-time State Management** with React Query
- **Accessibility Features** and keyboard navigation
- **Dark Mode Support** (configurable)

### Core Modules
1. **User Management** - User registration, authentication, and profile management
2. **Client Management** - Complete client relationship management
3. **Project Management** - Project tracking with status and priority management
4. **Financial Management** - Payments, expenses, and invoicing
5. **Dashboard & Analytics** - Overview with key metrics and insights
6. **Reporting** - Export capabilities for data analysis

## 🏗️ Project Structure

```
smart-crm-saas/
├── backend_restructured/           # FastAPI Backend
│   ├── app/
│   │   ├── core/                  # Core configuration and utilities
│   │   │   ├── config.py          # Application settings
│   │   │   ├── database.py        # Database configuration
│   │   │   └── security.py        # Authentication and security
│   │   ├── models/                # SQLAlchemy database models
│   │   │   ├── user_model.py      # User model
│   │   │   ├── client_model.py    # Client model
│   │   │   ├── project_model.py   # Project model
│   │   │   └── financial_model.py # Financial models
│   │   ├── schemas/               # Pydantic schemas for validation
│   │   │   ├── user_schemas.py    # User data schemas
│   │   │   ├── client_schemas.py  # Client data schemas
│   │   │   ├── project_schemas.py # Project data schemas
│   │   │   └── financial_schemas.py # Financial data schemas
│   │   └── api/                   # API endpoints
│   │       └── endpoints/         # Route handlers
│   │           ├── user_endpoints.py
│   │           ├── client_endpoints.py
│   │           ├── project_endpoints.py
│   │           └── financial_endpoints.py
│   ├── main.py                    # FastAPI application entry point
│   └── requirements.txt           # Python dependencies
├── frontend/                      # Next.js Frontend
│   ├── src/
│   │   ├── app/                   # Next.js App Router (pages, layouts, etc.)
│   │   ├── components/            # Reusable UI components
│   │   ├── contexts/              # React Contexts for global state
│   │   ├── lib/                   # Utility functions and libraries
│   │   ├── providers/             # React Context Providers
│   │   ├── types/                 # TypeScript type definitions
│   │   ├── middleware.ts          # Next.js middleware
│   │   └── setupTests.ts          # Jest setup file for tests
│   ├── tailwind.config.ts         # Tailwind CSS configuration
│   ├── package.json               # Node.js dependencies
│   └── .env.local                 # Environment variables
└── README.md                      # This file
```

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **Pydantic** - Data validation using Python type annotations
- **SQLite** - Lightweight database (easily replaceable with PostgreSQL)
- **Uvicorn** - ASGI server for production
- **Python-JOSE** - JWT token handling
- **Passlib** - Password hashing

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client for API requests
- **React Query** - Server state management
- **Lucide React** - Beautiful icons
- **Headless UI** - Unstyled, accessible UI components

## 🚀 Getting Started

### Prerequisites
- **Python 3.8+** for backend
- **Node.js 18+** for frontend
- **Git** for version control

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend_restructured
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the development server:**
   ```bash
   python main.py
   ```

   The backend will be available at: `http://localhost:8000`
   
   **API Documentation:** `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

   The frontend will be available at: `http://localhost:3000`

### Environment Configuration

Create a `.env.local` file in the frontend directory:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Smart CRM SaaS
```

## 📱 Usage

### Demo Credentials
For testing purposes, you can use these demo credentials:
- **Email:** `admin@example.com`
- **Password:** `admin123`

### Key Features Walkthrough

1. **Authentication**
   - Visit `http://localhost:3000`
   - Use demo credentials to log in
   - Experience protected routes and automatic redirects

2. **Dashboard**
   - View key metrics and statistics
   - See recent activities and quick actions
   - Navigate to different modules

3. **Client Management**
   - Add, edit, and delete clients
   - Search and filter client lists
   - View client details and project history

4. **Project Management**
   - Create and manage projects
   - Track project status and priority
   - Associate projects with clients

5. **Financial Management**
   - Record payments and expenses
   - Generate invoices
   - View financial analytics

## 🔧 API Endpoints

### Authentication
- `POST /api/v1/users/login` - User authentication
- `POST /api/v1/users/` - User registration

### Client Management
- `GET /api/v1/clients/` - List clients with pagination
- `POST /api/v1/clients/` - Create new client
- `GET /api/v1/clients/{id}` - Get client details
- `PUT /api/v1/clients/{id}` - Update client
- `DELETE /api/v1/clients/{id}` - Delete client

### Project Management
- `GET /api/v1/projects/` - List projects
- `POST /api/v1/projects/` - Create project
- `GET /api/v1/projects/{id}` - Get project details
- `PUT /api/v1/projects/{id}` - Update project
- `POST /api/v1/projects/{id}/complete` - Mark project as completed

### Financial Management
- `GET /api/v1/payments/` - List payments
- `POST /api/v1/payments/` - Record payment
- `GET /api/v1/expenses/` - List expenses
- `POST /api/v1/expenses/` - Add expense
- `GET /api/v1/financial/stats` - Financial statistics

## 🎨 UI Components

The frontend includes a comprehensive set of reusable UI components:

- **Button** - Multiple variants and sizes
- **Input** - Form inputs with validation states
- **Card** - Content containers with headers and footers
- **Loading** - Spinners, skeletons, and loading states
- **Layout** - Navigation and page structure components

## 🔒 Security Features

- **JWT Authentication** with secure token storage
- **Role-based Access Control** for different user types
- **Password Hashing** with bcrypt
- **CORS Configuration** for secure cross-origin requests
- **Input Validation** on both frontend and backend
- **SQL Injection Protection** through ORM usage

## 📊 Database Schema

The application uses a relational database with the following main entities:

- **Users** - Authentication and user management
- **Clients** - Customer information and contacts
- **Projects** - Project details and tracking
- **Payments** - Financial transactions
- **Expenses** - Business expense tracking
- **Invoices** - Billing and invoice management

## 🚀 Deployment

### Backend Deployment
```bash
# Install production dependencies
pip install uvicorn[standard]

# Run with Uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend Deployment
```bash
# Build for production
npm run build

# Start production server
npm start
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI** team for the excellent Python framework
- **Next.js** team for the React framework
- **Tailwind CSS** for the utility-first CSS framework
- **shadcn/ui** for the component design system inspiration

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the API documentation at `/docs`
- Review the component documentation in the code

---

**Built with ❤️ using modern web technologies**
