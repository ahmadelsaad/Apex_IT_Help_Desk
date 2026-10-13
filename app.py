import mysql.connector
from dotenv import load_dotenv
import os
import streamlit as st
import random


load_dotenv()
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')

connection = mysql.connector.connect(
    host = db_host,
    user = db_user,
    password = db_password,
    database = db_name
)

cursor=connection.cursor(dictionary=True)

cursor.execute('SELECT * FROM employee')
employees=cursor.fetchall()



cursor.execute('SELECT * FROM issue_category')
categories=cursor.fetchall()

cursor.execute('SELECT * FROM technician')
techs= cursor.fetchall()


st.title('Apex IT Help Desk')

view=st.sidebar.radio('View', ['Employee View','Technician View','Manager View'])


if view == 'Employee View':
    st.divider()
    st.subheader('Submit A Help Ticket')
    employee_names=[]
    for employee in employees:
        employee_names.append(employee['name'])

    selected_employee=st.selectbox('Employee',employee_names)

    issue_types=[]
    for category in categories:
        issue_types.append(category['category_name'])

    selected_category=st.selectbox('Issue Category',issue_types)

    issue_description=st.text_area('Issue Description')

    ppl_affected=st.number_input('Number of People Affected', min_value=1, step=1)

    impact_descript={'Minimal Impact': 'Minimal Impact — The issue is inconvenient, but I can perform all of my normal job tasks',
                    'Significant Impact': 'Significant Impact — The issue prevents me from performing some of my normal job tasks.',
                    'Severe Impact': 'Severe Impact — The issue prevents me from performing most or all of my normal job tasks.'}

    impact_levels=['Minimal Impact','Significant Impact','Severe Impact']
    work_impact=st.selectbox('How is your work impacted?', impact_levels, format_func=lambda x:impact_descript[x])


    workaround=['Yes','No']
    workaround_available=st.selectbox('Is there a temporary way for you to continue working?', workaround)

    if ppl_affected <=4:
        if (work_impact == 'Minimal Impact' or (work_impact=='Significant Impact' and workaround_available == 'Yes')):
            priority='Low'
        elif ((work_impact == 'Significant Impact' and workaround_available == 'No') or (work_impact == 'Severe Impact' and workaround_available == 'Yes')):
            priority='Medium'
        else:
            priority= 'High'
    elif ppl_affected <=9:
        if (work_impact == 'Minimal Impact' or (work_impact =='Significant Impact' and workaround_available == 'Yes')):
            priority='Medium'
        elif ((work_impact == 'Significant Impact' and workaround_available =='No') or (work_impact == 'Severe Impact' and workaround_available =='Yes')):
            priority='High'
        else:
            priority='Critical'
    else:
        if (work_impact == 'Minimal Impact' or (work_impact == 'Significant Impact' and workaround_available == 'Yes')):
            priority='High'
        else:
            priority='Critical'


    for employee in employees:
        if employee['name'] == selected_employee:
            selected_employee_id=employee['employee_id']

    for category in categories:
        if category['category_name']==selected_category:
            selected_category_id=category['category_id']
            selected_sector_id=category['sector_id']

    if workaround_available == 'Yes':
        workaround_value = 1
    else:
        workaround_value = 0


    sql_ticket= '''
    INSERT INTO ticket (employee_id, category_id, issue_desc, ppl_affected, work_impact, workaround, priority)
    VALUES(%s,%s,%s,%s,%s,%s,%s)
    '''


    values=(
        selected_employee_id,
        selected_category_id,
        issue_description,
        ppl_affected,
        work_impact,
        workaround_value,
        priority
    )

    sql_techs='''
    SELECT*
    FROM technician
    WHERE sector_id =%s AND availability = 1
    '''

    sql_tech_tickets = '''
    SELECT COALESCE(
        SUM(
            CASE
                WHEN ticket.priority = 'Low' THEN 1
                WHEN ticket.priority = 'Medium' THEN 4
                WHEN ticket.priority = 'High' THEN 7
                ELSE 0
            END
        ),
        0
    ) AS workload
    FROM ticket_assignment
    INNER JOIN ticket
    ON ticket_assignment.ticket_id = ticket.ticket_id
    WHERE ticket_assignment.tech_id = %s
    AND ticket.status != 'Closed'
    AND ticket_assignment.active_assignment = 1
    '''

    sql_last_assignment = '''
    SELECT MAX(assign_date_time) AS last_assignment
    FROM ticket_assignment
    WHERE ticket_assignment.tech_id = %s
    '''

    sql_assignment ='''
    INSERT INTO ticket_assignment (ticket_id, tech_id)
    VALUES (%s,%s)
    '''
    sql_update_status = '''
    UPDATE ticket
    SET status= 'Assigned'
    WHERE ticket_id = %s
    '''


    submitted_ticket=st.button('Submit Ticket')
    if submitted_ticket:
        if issue_description.strip() == '':
            st.error('Please Enter An Issue Description')
        elif len(issue_description)>500:
            st.error('Can Not Exceed 500 Characters')
        else:
            try:
                cursor.execute(sql_ticket, values)
                new_ticket_id=cursor.lastrowid
                

                if priority != 'Critical':
                    ticket_points={
                        'Low': 1,
                        'Medium': 4,
                        'High': 7
                    }[priority]
                    
                    cursor.execute(sql_techs, (selected_sector_id,))
                    avail_techs = cursor.fetchall()

                    if len(avail_techs) == 0:
                        connection.commit()
                        st.success('There Are No Available Technicians At This Time. Your Ticket Has Been Escalated To Leadership.')
                        
                    else:
                        tech_workloads = []
                        
                        for tech in avail_techs:
                            cursor.execute(sql_tech_tickets, (tech['tech_id'],))
                            workload_result = cursor.fetchone()
                            workload = workload_result['workload']

                            if workload + ticket_points <= 15:
                                tech_workloads.append({
                                    'tech_id': tech['tech_id'],
                                    'workload': workload
                                })

                        if len(tech_workloads) == 0:
                            connection.commit()
                            st.warning(
                            'All Qualified Technicians Are At Capacity. '
                            'Your Ticket Has Been Escalated To Leadership.')
                        

                        else:
                            least_work = min(tech['workload'] for tech in tech_workloads)
                                
                            least_tech_work = []

                            for tech in tech_workloads:
                                if tech['workload'] == least_work:
                                    least_tech_work.append(tech)

                            for tech in least_tech_work:
                                cursor.execute(sql_last_assignment, (tech['tech_id'],))
                                last_time_assigned = cursor.fetchone()
                                tech['last_assignment'] = last_time_assigned['last_assignment']

                            none_list = []

                            for tech in least_tech_work:
                                if tech['last_assignment'] is None:
                                    none_list.append(tech)

                            if len(none_list) != 0:
                                selected_tech = random.choice(none_list)

                            else:
                                last_assignment = min(
                                    tech['last_assignment'] for tech in least_tech_work
                                )
                                longest_wait_techs = []

                                for tech in least_tech_work:
                                    if tech['last_assignment'] == last_assignment:
                                        longest_wait_techs.append(tech)

                                selected_tech = random.choice(longest_wait_techs)

                            cursor.execute(
                                sql_assignment,
                                (new_ticket_id, selected_tech['tech_id'])
                            )

                            cursor.execute(
                                sql_update_status,
                                (new_ticket_id,)
                            )

                            connection.commit()
                            st.success('Thank You For Submitting Your Help Ticket')

                else:
                    connection.commit()
                    st.success('Critical Ticket Has Been Submitted And Escalated To Leadership')

            except mysql.connector.Error:
                connection.rollback()
                st.error('Ticket Submission Failed, Please Try Again')

    sql_resolved_tickets='''
    SELECT ticket.*,issue_category.category_name 
    FROM ticket
    INNER JOIN issue_category
    ON ticket.category_id = issue_category.category_id
    WHERE employee_id = %s
    AND status = 'Resolved'
    '''
    cursor.execute(sql_resolved_tickets,(selected_employee_id,))
    resolved_tickets=cursor.fetchall()

    st.divider()
    st.subheader('Ticket Confirmations')
    confirmation_info=[]

    for ticket in resolved_tickets:
        confirmation_row = {
            'Ticket ID': ticket['ticket_id'],
            'Issue Category': ticket['category_name']
        }
        confirmation_info.append(confirmation_row)

    if len(confirmation_info) > 0:
        st.dataframe(confirmation_info)
    confirmation_ids=[]
    
    for ticket in resolved_tickets:
        confirmation_ids.append(ticket['ticket_id'])
    
    if len(confirmation_ids) >0:
        selected_confirmation_id = st.selectbox('Select Ticket', confirmation_ids)
        for ticket in resolved_tickets:
            if ticket['ticket_id'] == selected_confirmation_id:
                selected_confirmation = ticket
        
        st.subheader(f"Ticket #{selected_confirmation['ticket_id']}")
        st.write(f"**Issue Description:** {selected_confirmation['issue_desc']}")

    
        answer = st.selectbox(
            'Has Your Issue Been Resolved?',
            ['Select An Answer:', 'Yes', 'No'],
            key=f"confirm_{selected_confirmation['ticket_id']}"
        )
        if answer == 'Yes':
            confirm_resolution = st.button(
            'Confirm Resolution',
            key=f"close_{selected_confirmation['ticket_id']}"
            )

            if confirm_resolution:
                sql_confirm_resolution = '''
                UPDATE ticket
                SET status = 'Closed'
                WHERE ticket_id = %s
                '''

                cursor.execute(sql_confirm_resolution, (selected_confirmation['ticket_id'],))
                connection.commit()
                st.rerun()
        elif answer == 'No':
            employee_feedback = st.text_area(
            'What Issue Are You Still Experiencing?',
            key=f"issue_cont_{selected_confirmation['ticket_id']}")
                
            submit_feedback = st.button(
            'Submit Feedback',
            key=f"feedback_{selected_confirmation['ticket_id']}")

            if submit_feedback:
                if employee_feedback.strip() == '':
                    st.error('Please Make Sure To Write What The Issue Is')
                elif len(employee_feedback) >200:
                    st.error('Can Not Exceed 200 Characters')
                else:
                    sql_employee_feedback = '''
                    UPDATE ticket
                    SET status = 'In Progress',
                    emp_update = %s
                    WHERE ticket_id = %s
                    '''

                    cursor.execute(
                    sql_employee_feedback,
                    (employee_feedback, selected_confirmation['ticket_id']))
         
                    connection.commit()
                    st.rerun()
    else:
        st.write('No Tickets Awaiting Confirmation')

                


elif view == 'Technician View':
    st.header('Technician Dashboard')
    st.divider()
    technician_names=[]
    for tech in techs:
        technician_names.append(tech['tech_name'])
    selected_technician=st.selectbox('Technician', technician_names)

    for tech in techs:
        if tech['tech_name'] == selected_technician:
            selected_technician_id = tech['tech_id']

    sql_assigned_tickets = '''
    SELECT *
    FROM ticket
    INNER JOIN ticket_assignment
    ON ticket.ticket_id = ticket_assignment.ticket_id
    INNER JOIN issue_category
    ON ticket.category_id=issue_category.category_id
    INNER JOIN employee
    ON ticket.employee_id = employee.employee_id 
    WHERE ticket_assignment.tech_id = %s
    AND ticket_assignment.active_assignment = 1
    AND ticket.status != 'Closed'
    '''

    cursor.execute(sql_assigned_tickets,(selected_technician_id,))
    assigned_tickets=cursor.fetchall()

    st.subheader('Assigned Tickets')
    ticket_info=[]

    for ticket in assigned_tickets:
        ticket_row={
            'Ticket ID': ticket['ticket_id'],
            'Priority': ticket['priority'],
            'Status': ticket['status'],
            'Category': ticket['category_name']
        }
        ticket_info.append(ticket_row)
    st.dataframe(ticket_info)

    st.divider()
    ticket_ids = []
    for ticket in assigned_tickets:
        ticket_ids.append(ticket['ticket_id'])

    if len(ticket_ids)>0:
        selected_ticket_id = st.selectbox('Select Ticket', ticket_ids)

        for ticket in assigned_tickets:
            if ticket['ticket_id'] == selected_ticket_id:
                selected_ticket = ticket

        ticket=selected_ticket
        
        st.subheader(f"Ticket #{ticket['ticket_id']}")
        
        if ticket['workaround']:
            workaround_display = 'Yes'
        else:
            workaround_display = 'No'
        
        col1,col2 = st.columns(2)
        with col1:
            st.write(f"**Employee Name:** {ticket['name']}")
            st.write(f"**Status:** {ticket['status']}")
            st.write(f"**Time Submitted:** {ticket['ticket_date_time']}")
            
        with col2:
            st.write(f"**Work Impact:** {ticket['work_impact']}")
            st.write(f"**People Affected:** {ticket['ppl_affected']}")
            st.write(f"**Workaround Available:** {workaround_display}")
        st.write(f"**Issue Description:** {ticket['issue_desc']}")

        if ticket['emp_update'] is not None and ticket['status'] == 'In Progress':
            st.warning('Employee Reported Issue Is Still Occurring')

    
        if ticket['emp_update'] is not None:
            st.write(f"**Employee Update:** {ticket['emp_update']}")
                
        if ticket['status'] == 'Assigned':
            start_work = st.button('Start Work', key=f"start_{ticket['ticket_id']}")

            if start_work:
                sql_start_work = '''
                UPDATE ticket
                SET status = 'In Progress'
                WHERE ticket_id = %s
                '''
                        
                cursor.execute(sql_start_work, (ticket['ticket_id'],))
                connection.commit()
                st.rerun()
                    
        if ticket['status'] == 'In Progress':
            resolved=st.button('Issue Resolved', key=f"resolve_{ticket['ticket_id']}")

            if resolved:
                sql_issue_resolved = '''
                UPDATE ticket
                SET status = 'Resolved'
                WHERE ticket_id = %s
                '''

                cursor.execute(sql_issue_resolved, (ticket['ticket_id'],))
                connection.commit()
                st.rerun()

        if ticket['status'] == 'Resolved':
            st.info('Waiting for Employee Confirmation')
    else:
        st.write('No Assigned Tickets')





elif view == 'Manager View':
    st.header('Manager Dashboard')

    sql_all_tickets = '''
    SELECT ticket.ticket_id, ticket.priority, ticket.status,
    ticket.ticket_date_time, ticket.issue_desc,
    ticket.ppl_affected, ticket.work_impact, employee.name,
    issue_category.category_name, ticket.workaround,
    ticket.emp_update, issue_category.sector_id,
    GROUP_CONCAT(technician.tech_name SEPARATOR ', ') AS assigned_technicians
    FROM ticket
    INNER JOIN employee
    ON ticket.employee_id = employee.employee_id
    INNER JOIN issue_category
    ON ticket.category_id = issue_category.category_id
    LEFT JOIN ticket_assignment
    ON ticket.ticket_id = ticket_assignment.ticket_id
    AND ticket_assignment.active_assignment = 1
    LEFT JOIN technician
    ON ticket_assignment.tech_id = technician.tech_id
    GROUP BY ticket.ticket_id, ticket.priority, ticket.status,
    ticket.ticket_date_time, ticket.issue_desc,
    ticket.ppl_affected, ticket.work_impact, employee.name,
    issue_category.category_name, ticket.workaround,
    ticket.emp_update, issue_category.sector_id
    '''

    cursor.execute(sql_all_tickets)
    all_tickets = cursor.fetchall()

    open_tickets=0

    for ticket in all_tickets:
        if ticket['status'] != 'Closed':
            open_tickets +=1

    critical_tickets=0

    for ticket in all_tickets:
        if ticket['priority'] =='Critical' and ticket['status'] != 'Closed':
            critical_tickets +=1
    
    available_techs = 0

    for tech in techs:
        if tech['availability'] == 1:
            available_techs += 1
    
    col1,col2,col3=st.columns(3)
    col1.metric('Open Tickets', open_tickets)
    col2.metric('Critical Tickets', critical_tickets)
    col3.metric('Available Technicians', available_techs)

    st.divider()
    st.subheader('Ticket Management')
    col1,col2=st.columns(2)

    with col1:
        priority_filter = st.selectbox('Filter By Priority', ['All', 'Low', 'Medium', 'High', 'Critical'])
    with col2:
        status_filter = st.selectbox('Filter By Status', ['All', 'New', 'Assigned', 'In Progress', 'Resolved', 'Closed'])

    filtered_tickets = []

    
    for ticket in all_tickets:
        if priority_filter == 'All' or ticket['priority'] == priority_filter:
            if status_filter == 'All' or ticket['status'] == status_filter:
                filtered_tickets.append(ticket)
    
    table_tickets=[]
    for ticket in filtered_tickets:
        ticket_row = {
            'Ticket ID': ticket['ticket_id'],
            'Priority': ticket['priority'],
            'Status': ticket['status'],
            'Date Submitted': ticket['ticket_date_time'],
            'Assigned Technician': ticket['assigned_technicians']}
        table_tickets.append(ticket_row)
    st.dataframe(table_tickets)
    
    ticket_ids = []

    for ticket in filtered_tickets:
        ticket_ids.append(ticket['ticket_id'])

    if len(ticket_ids) > 0:
        selected_ticket_id = st.selectbox('Select Ticket', ticket_ids)
    
        for ticket in filtered_tickets:
            if ticket['ticket_id'] == selected_ticket_id:
                selected_ticket = ticket 

        st.subheader(f"Ticket #{selected_ticket['ticket_id']}")

        if selected_ticket['workaround']:
            man_workaround = 'Yes'
        else:
            man_workaround = 'No'
        
        
        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Priority:** {selected_ticket['priority']}")
            st.write(f"**Employee Name:** {selected_ticket['name']}")
            st.write(f"**People Affected:** {selected_ticket['ppl_affected']}")
            st.write(f"**Workaround Available:** {man_workaround}")
        with col2:
            st.write(f"**Status:** {selected_ticket['status']}")
            st.write(f"**Category:** {selected_ticket['category_name']}")
            st.write(f"**Work Impact:** {selected_ticket['work_impact']}")
        st.write(f"**Description:** {selected_ticket['issue_desc']}")

        st.divider()
        st.subheader('Technician Assignment')
        
        if selected_ticket['assigned_technicians'] is None:
            st.write('Technician Assigned: Unassigned')
        else:
            st.write(f"Technician Assigned: {selected_ticket['assigned_technicians']}")

    




        ticket = selected_ticket

        if ticket['emp_update'] is not None:
            st.write(f"Employee Update: {ticket['emp_update']}")

        if ticket['status'] in ['Resolved', 'Closed']:
            st.info('This Ticket Cannot Be Reassigned')

        else:
            qualified_techs = []

            for tech in techs:
                if tech['sector_id'] == ticket['sector_id'] and tech['availability'] == 1:
                    qualified_techs.append(tech)

            qualified_tech_names = []

            for tech in qualified_techs:
                qualified_tech_names.append(tech['tech_name'])

            if len(qualified_tech_names) == 0:
                st.warning('No Available Technicians')

            else:
                manager_selected_tech = st.selectbox(
                    'Select Technician',
                    qualified_tech_names,
                    key=f"select_tech_{ticket['ticket_id']}")
                

                for tech in qualified_techs:
                    if tech['tech_name'] == manager_selected_tech:
                        manager_selected_tech_id = tech['tech_id']

                sql_deactivate_assignment = '''
                UPDATE ticket_assignment
                SET active_assignment = 0
                WHERE ticket_id = %s
                AND active_assignment = 1
                '''

                sql_ticket_assignment = '''
                INSERT INTO ticket_assignment (ticket_id, tech_id)
                VALUES (%s, %s)
                '''

                sql_manager_update = '''
                UPDATE ticket
                SET status = 'Assigned'
                WHERE ticket_id = %s
                '''
                    
                assign_tech = st.button(
                    'Assign Technician',
                    key=f"assign_{ticket['ticket_id']}")
                

                if assign_tech:
                    sql_check_assignment = '''
                    SELECT ticket_id, tech_id
                    FROM ticket_assignment
                    WHERE ticket_id = %s
                    AND tech_id = %s
                    AND active_assignment = 1
                    '''

                    cursor.execute(
                        sql_check_assignment,
                        (ticket['ticket_id'], manager_selected_tech_id))
                        
                    existing_assignment = cursor.fetchone()

                    if existing_assignment is not None:
                        st.warning(
                            'This Technician Is Already Assigned To This Ticket')
                            
                    else:
                        if ticket['priority'] != 'Critical':
                            cursor.execute(
                                sql_deactivate_assignment,
                                (ticket['ticket_id'],))
                                
                        cursor.execute(
                            sql_ticket_assignment,
                            (ticket['ticket_id'], manager_selected_tech_id))
                            
                        if ticket['priority'] != 'Critical' or ticket['status'] == 'New':
                            cursor.execute(
                                sql_manager_update,
                                (ticket['ticket_id'],))
                                
                        connection.commit()
                        st.rerun()

    else:
        st.info('No Tickets Match The Selected Filters')

    st.divider()
    st.subheader('Technician Availability')
    

    sql_update_availability = '''
    UPDATE technician
    SET availability = %s
    WHERE tech_id = %s
    '''

    availability_tech_names = []

    for tech in techs:
        availability_tech_names.append(tech['tech_name'])

    col1,col2 =st.columns(2)
    with col1:
        selected_tech_available = st.selectbox(
            'Select A Technician',
            availability_tech_names)

    selected_availability_tech_id = None

    for tech in techs:
        if tech['tech_name'] == selected_tech_available:
            selected_availability_tech_id = tech['tech_id']
            current_availability=tech['availability']
            if tech['availability'] == 1:
                current_availability='Available'
            else:
                current_availability='Unavailable'
    st.write(f"Technician Availability: {current_availability}")


    with col2:
        selected_availability = st.selectbox(
            'Select Availability',
            ['Yes', 'No'])

    if selected_availability == 'Yes':
        availability_value = 1
    else:
        availability_value = 0

    update_available = st.button('Update Availability')

    if update_available:
        cursor.execute(
            sql_update_availability,
            (availability_value, selected_availability_tech_id))
        connection.commit()
        st.rerun()


