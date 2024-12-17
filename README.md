# TeaFarmPro

## Overview

The Tea Farm Management System is designed to streamline the management of tea farms by providing a suite of tools for tracking production, managing inventory, assigning tasks, and more. This system aims to improve the efficiency of farm operations and enhance productivity through comprehensive data management and reporting features.

## Features

### Farm Overview Dashboard
- **Production Summary**: Overview of recent production statistics (e.g., total yield, average yield per acre).
- **Workforce Summary**: Labor activities, including tasks assigned and completed.

### Task Management
- **Assign Tasks to Employees**: 
  - Form to assign specific tasks (e.g., weeding, plucking) to employees with fields for task description, employee(s) assigned, start date, due date, and priority level.
- **Track Task Progress**: 
  - Widget or form to update the status of ongoing tasks with fields for Task ID, current status, and notes.

### Production Management
- **Record Daily Production**: 
  - Form to enter daily production data with fields for Date, quantity of tea leaves plucked, employee(s) responsible, and notes.
- **View Historical Production Data**: 
  - Search or filter form to view past production records.

### Inventory Management
- **Add/Edit Inventory**: 
  - Form to manage inventory items (e.g., fertilizers, tools) with fields for Item name, quantity, purchase date, and supplier details.
- **Track Inventory Usage**: 
  - Form to log the usage of inventory items with fields for Item, quantity used, date, and purpose.

### Expense Tracking
- **Log Operational Expenses**: 
  - Form to log expenses related to farm operations with fields for Date, expense type, amount, payment method, and notes.

### Employee Management
- **Add New Employee**: 
  - Form to register new employees with fields for Name, role, contact details, and start date.
- **Edit Employee Details**: 
  - Form to update the details of existing employees with fields for Employee ID and updated information.

### Reporting
- **Generate Reports**: 
  - Form to generate various reports (e.g., production reports, expense reports) with fields for Report type, date range, and output format (PDF, CSV).

### Profile Management
- **Update Farmer Profile**: 
  - Form to update farmer profile details with fields for Name, email, phone number, and farm details.
## Forms and Their Usage

### 1. Farm Overview Dashboard
- **Production Summary**: Provides a snapshot of recent production metrics.
- **Workforce Summary**: Displays details about labor activities, including tasks and their statuses.

### 2. Task Management
- **Assign Tasks to Employees**:
  - **Purpose**: To allocate specific tasks to farm employees.
  - **Fields**:
    - **Task Description**: A brief description of the task.
    - **Employee(s) Assigned**: The employee or employees assigned to the task.
    - **Start Date**: When the task begins.
    - **Due Date**: Deadline for task completion.
    - **Priority Level**: Importance of the task (e.g., High, Medium, Low).
- **Track Task Progress**:
  - **Purpose**: To monitor and update the status of tasks.
  - **Fields**:
    - **Task ID**: Unique identifier for the task.
    - **Current Status**: Current status (e.g., In Progress, Completed).
    - **Notes**: Additional comments or updates.

### 3. Production Management
- **Record Daily Production**:
  - **Purpose**: To log daily production details.
  - **Fields**:
    - **Date**: Date of production.
    - **Quantity of Tea Leaves Plucked**: Amount of tea leaves harvested.
    - **Employee(s) Responsible**: Employee or employees who did the work.
    - **Notes**: Additional remarks.
- **View Historical Production Data**:
  - **Purpose**: To access and review past production records.
  - **Features**: Search and filter capabilities to view historical data.

### 4. Inventory Management
- **Add/Edit Inventory**:
  - **Purpose**: To manage inventory items.
  - **Fields**:
    - **Item Name**: Name of the inventory item.
    - **Quantity**: Number of items in stock.
    - **Purchase Date**: Date when the item was bought.
    - **Supplier Details**: Information about the supplier.
- **Track Inventory Usage**:
  - **Purpose**: To record how inventory items are used.
  - **Fields**:
    - **Item**: Name of the inventory item used.
    - **Quantity Used**: Amount of item used.
    - **Date**: Date of usage.
    - **Purpose**: Reason for usage.

### 5. Expense Tracking
- **Log Operational Expenses**:
  - **Purpose**: To record expenses incurred during farm operations.
  - **Fields**:
    - **Date**: Date of the expense.
    - **Expense Type**: Category of the expense.
    - **Amount**: Amount spent.
    - **Payment Method**: Method of payment used.
    - **Notes**: Additional details about the expense.

### 6. Employee Management
- **Add New Employee**:
  - **Purpose**: To register new employees.
  - **Fields**:
    - **Name**: Full name of the employee.
    - **Role**: Job role or title.
    - **Contact Details**: Phone number and email address.
    - **Start Date**: Date when the employee starts.
- **Edit Employee Details**:
  - **Purpose**: To update information for existing employees.
  - **Fields**:
    - **Employee ID**: Unique identifier for the employee.
    - **Updated Information**: New or revised details.

### 7. Reporting
- **Generate Reports**:
  - **Purpose**: To create various types of reports.
  - **Fields**:
    - **Report Type**: Type of report to generate (e.g., Production Report, Expense Report).
    - **Date Range**: Time period for the report.
    - **Output Format**: Format of the report (e.g., PDF, CSV).

### 8. Profile Management
- **Update Farmer Profile**:
  - **Purpose**: To modify farmer profile details.
  - **Fields**:
    - **Name**: Full name of the farmer.
    - **Email**: Email address.
    - **Phone Number**: Contact phone number.
    - **Farm Details**: Information about the farm.

## Database Schema

### Tables

- **employees**: Information about farm employees.
- **farmers**: Details of farmers using the system.
- **labours**: Details about different labor types and rates.
- **market_value**: Market value of tea leaves.
- **plucking_outputs**: Records of tea leaves plucked.
- **transport_costs**: Costs associated with transport.
- **weeding_outputs**: Records of weeding activities.

### Key Fields in Tables

- **labours**:
  - `type`: Type of labor (e.g., weeding, plucking).
  - `rate`: Rate for the labor type.
  - `id`: Unique identifier.
  - `created_at` / `updated_at`: Timestamps.

- **market_value**:
  - `date`: Date of market value record.
  - `value_per_kg`: Market value per kilogram.
  - `daily_weight`: Weight of tea leaves for the day.
  - `id`: Unique identifier.
  - `created_at` / `updated_at`: Timestamps.

- **plucking_outputs**:
  - `employee_id`: Identifier for the employee who did the plucking.
  - `date`: Date of plucking.
  - `weight`: Weight of tea leaves plucked.
  - `payment`: Payment calculated based on the labor rate.
  - `id`: Unique identifier.
  - `created_at` / `updated_at`: Timestamps.

- **weeding_outputs**:
  - `employee_id`: Identifier for the employee who did the weeding.
  - `date`: Date of weeding.
  - `area_covered`: Area covered by weeding.
  - `payment`: Payment calculated based on the labor rate.
  - `id`: Unique identifier.
  - `created_at` / `updated_at`: Timestamps.

- **transport_costs**:
  - `description`: Description of the transport cost.
  - `amount`: Amount incurred.
  - `id`: Unique identifier.
  - `created_at` / `updated_at`: Timestamps.

## Setup and Installation


1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/teafarm_pro.git
   cd teafarm_pro
2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
3. **Configure the Database:**
   ```bash
   Update the database configuration in config/database.py. 
4. **Run Migrations:**
   ```bash
   python manage.py migrate

5. **Start the Development Server:**
   ```bash
   python manage.py runserver
6. **Access the Application:**
   ```bash
   - Open a web browser and go to http://127.0.0.1:8000 to access the application.

## Usage

1. **Login:**
   - Navigate to the login page and enter your credentials.
     
2. **Dashboard:**
   - Access the Farm Overview Dashboard to view production and workforce summaries.
     
3. **Manage Tasks:**
   - Assign and track tasks from the Task Management section.

4. **Production Management**:
   - Record daily production data and view historical production records.

5. **Inventory Management**:
   - Add or edit inventory items and track their usage.

6. **Expense Tracking**:
   - Log operational expenses with details.

7. **Employee Management**:
   - Add new employees and edit existing employee details.

8. **Reporting**:
   - Generate various reports based on the required criteria.

9. **Profile Management**:
   - Update your profile details as necessary.

## Contributing

We welcome contributions to the Tea Farm Management System. To contribute:

1. **Fork the Repository**: Click the "Fork" button on GitHub to create a personal copy of the repository.
2. **Clone Your Fork**: Clone your forked repository to your local machine.
   ```bash
   git clone https://github.com/yourusername/teafarm_pro.git

## Project documentation

Please find links to important project documentation:
1. Project status updater: https://docs.google.com/document/d/1kLKk-K16MqD1fRdvlniio0ah-gAugpn0br787ic2ibE/edit?usp=sharing
2. Project proposal: https://docs.google.com/document/d/1PxQVhFgOZnNV9uwBWsavlVZuGkOZOvfG0-sLBMCu-8c/edit?usp=sharing
3. Trello dashboard: https://trello.com/b/HNYWhxKL/teafarm-pro
4. Project articles: https://eodenyire.medium.com/revolutionizing-tea-farm-management-the-teafarmpro-project-fa0be9a88bab

## Contact

For any questions or support, please contact:

- **Emmanuel Odenyire Anyira**
  - [LinkedIn](https://www.linkedin.com/in/emmanuelodenyire/)
  - [GitHub](https://github.com/eodenyire)
  - Email: [eodenyire@gmail.com](mailto:eodenyire@gmail.com)

- **Daniel Kipkosgei**
  - [LinkedIn](https://www.linkedin.com/in/daniel-kipkosgei-2ab84117b/)
  - [GitHub](https://github.com/Chirchir-Dan)
  - Email: [dkipkosgei.daniel@gmail.com](mailto:dkipkosgei.daniel@gmail.com)

- **David King'asia**
  - [LinkedIn](https://www.linkedin.com/in/davidkingasia/)
  - [GitHub](https://github.com/Dev-Kings)
  - Email: [kingasiadavid41@gmail.com](mailto:kingasiadavid41@gmail.com)

- **Joy Wanjiru Muchemi**
  - [GitHub](https://github.com/muchemiwanjiru)

   
