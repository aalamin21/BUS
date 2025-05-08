
# StudyBuddy: Your Study Group Organiser

## Brief Description of the System and Its Purpose

**StudyBuddy** is an educational matchmaker, designed for university students to collaborate within the same modules and cohort. The system encourages peer-to-peer support by forming small study groups (4–6 members) that align with students’ learning goals and schedules.

Currently, StudyBuddy focuses on supporting first-year medical students at the University of Birmingham. It helps reduce feelings of isolation and enhances academic engagement outside formal teaching settings, as emphasized in relevant literature.

Through a user-friendly web interface, students can submit module choices and preferred study times. The system then recommends groups with similar academic interests and compatible schedules. After group formation, the system books a study room and prompts members to utilize that time and space for collaborative study.

StudyBuddy fosters inclusive, supportive peer collaboration—serving as both a social connector and academic aid. It helps build community and provides a structured approach to shared learning beyond lecture theatres.

---

## Step-by-Step Instructions on How to Run the Project

```bash
pip install -r requirements.txt
flask shell
reset_db()  # To initialise database with testing data
# Exit the shell: Ctrl+D (Linux/macOS) or Cmd+D (macOS)
flask run
```

---

## List of Programming Languages, Frameworks, or Tools Used

- Python  
- HTML  
- CSS  
- Flask  
- SQLAlchemy  
- Pytest  
- Jinja  

---

## Summary of Implemented Functionalities

### Profile Creation
Upon launching the system, users fill out a registration form to provide:
- Their availability
- Selected course and challenging modules (via dropdown)
- University email

The default course is *Medicine and Surgery MBChB*, with available modules being First Year options in this course.

### Jaccard Similarity Algorithm for Group Formation
The system uses:
- Availability data
- Selected module data

Two algorithms run concurrently to group users based on compatible schedules and study interests. Users can select up to three modules and input as much or as little availability as they wish. If no suitable group is found or existing ones are full, users can create their own group.

This approach differs from an earlier proposed clustering method, with the similarity-based method proving more practical.

### Room Booking Functionality
Once in a group, users:
- See a list of overlapping available times
- View available Group Study Rooms
- One member books a suitable time slot, which is reserved for all group members

---

## Contribution Table

| Student Name     | ID Number | Contribution (%) | Key Contributions / Tasks Completed                                                                                                       | Signature |
|------------------|-----------|------------------|-------------------------------------------------------------------------------------------------------------------------------------------|-----------|
| Rajan Dosanjh    | 2735127   | 20%              | Profile creation (first registration page), full HTML page design, student DB creation, room booking functionality, video editing, README | RD        |
| Kelby Matthew    | 2884840   | 20%              | Grouping algorithm, HTML for suggested/joined group pages, leaving group functionality                                                    | KM        |
| Alfred Mureithi  | 2185431   | 20%              | Test cases for features, HTML and page creation for 'Suggest Meeting Time' page                                                           | AM        |
| Irfan Hassan     | 2066182   | 20%              | Group suggestion algorithm, HTML for suggested/joined group pages                                                                         | IH        |
| Ahmed Alamin     | 2005390   | 20%              | Availability editing page (HTML/backend), booking add/delete functionality, database class models, general debugging                      | AA        |
