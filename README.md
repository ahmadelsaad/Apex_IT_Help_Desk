# Apex IT Help Desk

Apex IT Help Desk is a ticket management and reporting system I built for a fictional company, Apex Industries. The goal of this project was to create a system that could manage employee IT requests, automatically assign tickets to technicians, and provide managers with information about ticket volume and technician workloads.

The project uses Python, MySQL, and Streamlit for the help desk application, along with Power BI for reporting and analysis.

## How the System Works

Employees can submit IT support requests by selecting an issue category and providing information about the problem. The system uses the number of people affected, business impact, and availability of a workaround to determine the ticket's priority.

Tickets are then assigned to technicians based on their IT specialization, availability, and current workload. When multiple technicians qualify, the system selects the technician with the lowest weighted workload. If there is a tie, it considers how long each technician has gone without receiving an assignment.

Technicians can update their assigned tickets as they work on them. Once a ticket is marked as resolved, the employee can confirm whether the issue was fixed. If the issue remains unresolved, the ticket returns to In Progress.

The application also includes a manager view for monitoring tickets, technician availability, and assignments.

## Database

I designed a relational database in MySQL with six tables:

- **employee:** Employee information and departments
- **technician:** Technician information, specialization, and availability
- **it_sector:** IT support sectors
- **issue_category:** Types of IT issues and their corresponding sectors
- **ticket:** Support requests, priorities, and statuses
- **ticket_assignment:** Technician assignments and assignment history

The database uses primary and foreign keys to connect the tables and maintain relationships between employees, tickets, and technicians.

## Power BI Dashboard

I also created a three-page Power BI dashboard to analyze IT support operations using 500 simulated support tickets.

### Page 1: Executive Overview

Provides an overview of ticket performance, including total tickets, open and closed tickets, closure rate, ticket priorities, and ticket aging.

### Page 2: Technician Performance & Workload

Shows active technician assignments, unassigned tickets, and how workloads are distributed across technicians and IT sectors.

### Page 3: Ticket Demand & Issue Analysis

Analyzes weekly ticket volume, the most common issue categories, and categories generating high-priority requests. This page also includes filters for department, IT sector, and date range.

## Technologies Used

- **Python:** Ticket processing and automated assignment logic
- **MySQL:** Database design and storage
- **SQL:** Database queries and data management
- **Streamlit:** Application interface
- **Power BI:** Interactive reporting and dashboards
- **DAX:** Calculated measures and performance metrics

## Running the Application

Clone the repository:

```bash
git clone https://github.com/ahmadelsaad/Apex_IT_Help_Desk.git
cd Apex_IT_Help_Desk
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Set up the MySQL database using the provided SQL files and configure the database connection in a local `.env` file.

Start the Streamlit application:

```bash
streamlit run app.py
```

## What I Learned

This project gave me experience building a system from the initial planning and database design stages through application development and reporting.

I worked with relational databases, Python automation, business rules, and application workflows. I also gained experience using Power BI and DAX to turn operational data into reports that could help managers identify backlogs, monitor technician workloads, and understand support demand.

The project uses a fictional company and simulated data for demonstration purposes.
