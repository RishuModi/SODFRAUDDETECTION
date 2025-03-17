
This C++ program is designed to detect conflicts in user roles and privileges based on Segregation of Duties (SOD) rules. It reads data from CSV files, processes mappings between users, roles, privileges, and entities, and checks for conflicts using predefined SOD rules. The program outputs detected conflicts to a CSV file for further analysis.

Features
CSV Data Loading: Reads user-to-role, role-to-privilege, and privilege-to-entity mappings from CSV files.

SOD Rule Enforcement: Loads and enforces SOD rules to detect conflicting privileges assigned to users.

Conflict Detection: Identifies conflicts using exact and substring matching for privileges.

Output Generation: Generates a CSV file containing detected conflicts with details like user, role, privilege, entity, and position.

Debugging Tools: Includes a debug mode to print loaded mappings for verification.

How It Works
Input Files:

XX_3_USER_ROLE_MAPPING_RPT.csv: Maps users to their assigned roles.

XX_6_PVLG_TO_ROLE_RELATION_RPT.csv: Maps roles to their associated privileges.

XX_7_PVLGS_MASTER_RPT.csv: Maps privileges to their associated entities.

SOD_Ruleset.csv: Contains SOD rules defining conflicting privileges.

Process:

Loads CSV data into appropriate data structures.

Iterates through users, roles, and privileges to detect conflicts using SOD rules.

Writes detected conflicts to an output CSV file (conflict_results.csv).

Conflict Detection Logic:

Checks for exact matches between privileges in SOD rules.

Performs substring matching to identify partial conflicts (e.g., CREATE_USER conflicts with DELETE_USER).

Getting Started
Prerequisites
C++ Compiler: Ensure you have a C++ compiler installed (e.g., g++).

CSV Files: Prepare the input CSV files as described above.

Steps to Run
Clone the Repository:

git clone https://github.com/your-username/sod-conflict-detector.git
cd sod-conflict-detector
Compile the Program:


g++ -o sod_detector main.cpp
Run the Program:


./sod_detector
Check Output:

The program will generate a file named conflict_results.csv containing detected conflicts.

Input File Formats
1. User-to-Role Mapping (XX_3_USER_ROLE_MAPPING_RPT.csv)
Format:

User,Role
user1,role1
user2,role2
2. Role-to-Privilege Mapping (XX_6_PVLG_TO_ROLE_RELATION_RPT.csv)
Format:


Role,Privilege
role1,privilege1
role1,privilege2
3. Privilege-to-Entity Mapping (XX_7_PVLGS_MASTER_RPT.csv)
Format:


Privilege,Entity
privilege1,entity1
privilege2,entity2
4. SOD Rules (SOD_Ruleset.csv)
Format:


RuleID,Privilege1,Privilege2,Description
1,CREATE_USER,DELETE_USER,User management conflict
2,APPROVE_PAYMENT,CREATE_PAYMENT,Payment processing conflict
Output File Format
Conflict Results (conflict_results.csv)
Format:


User,Role,Privilege,Entity,Position
user1,role1,CREATE_USER,User Management,High-Risk
user2,role2,APPROVE_PAYMENT,Payment Processing,High-Risk
Example
Input Files
XX_3_USER_ROLE_MAPPING_RPT.csv:


User,Role
alice,admin
bob,auditor
XX_6_PVLG_TO_ROLE_RELATION_RPT.csv:


Role,Privilege
admin,CREATE_USER
admin,DELETE_USER
auditor,APPROVE_PAYMENT
XX_7_PVLGS_MASTER_RPT.csv:


Privilege,Entity
CREATE_USER,User Management
DELETE_USER,User Management
APPROVE_PAYMENT,Payment Processing
SOD_Ruleset.csv:


RuleID,Privilege1,Privilege2,Description
1,CREATE_USER,DELETE_USER,User management conflict
Output File (conflict_results.csv)
Copy
User,Role,Privilege,Entity,Position
alice,admin,CREATE_USER,User Management,High-Risk
alice,admin,DELETE_USER,User Management,High-Risk

Debugging
To debug and verify the loaded mappings, enable the debugPrintMappings function in the main function. It will print the following:

SOD Rules

User-to-Roles Mapping

Role-to-Privileges Mapping

Contributing
Contributions are welcome! If you find any issues or have suggestions for improvement, please open an issue or submit a pull request.


Acknowledgments
Inspired by real-world SOD conflict detection systems.

Built with C++ for performance and simplicity.

Contact
For questions or feedback, feel free to reach out:

GitHub: https://github.com/RishuModi
Email: rishumodi1001@gmail.com
Enjoy using the SOD Conflict Detector! 🚀
