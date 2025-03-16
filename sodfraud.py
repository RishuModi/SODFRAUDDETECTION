#include <iostream>
#include <fstream>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <sstream>

using namespace std;

// Data structures to store role, privilege, and conflict rules
unordered_map<string, vector<string>> roleToPrivileges;
unordered_map<string, vector<string>> userToRoles;
unordered_map<string, string> privilegeToEntity;
unordered_map<string, unordered_set<string>> sodRules; // Conflict rules

struct ConflictEntry {
    string user;
    string role;
    string privilege;
    string entity;
    string position;
};

vector<ConflictEntry> conflicts;

// Function to load CSV data (multi-value map)
void loadCSVData(const string& filename, unordered_map<string, vector<string>>& data, int keyCol, int valueCol) {
    ifstream file(filename);
    if (!file.is_open()) {
        cerr << "❌ Error opening CSV file: " << filename << endl;
        return;
    }

    string line;
    while (getline(file, line)) {
        stringstream ss(line);
        vector<string> row;
        string cell;
        while (getline(ss, cell, ',')) {
            row.push_back(cell);
        }
        if (row.size() > max(keyCol, valueCol)) {
            data[row[keyCol]].push_back(row[valueCol]);
        }
    }
    file.close();
}

// Function to load single-value CSV data
void loadCSVData(const string& filename, unordered_map<string, string>& data, int keyCol, int valueCol) {
    ifstream file(filename);
    if (!file.is_open()) {
        cerr << "❌ Error opening CSV file: " << filename << endl;
        return;
    }

    string line;
    while (getline(file, line)) {
        stringstream ss(line);
        vector<string> row;
        string cell;
        while (getline(ss, cell, ',')) {
            row.push_back(cell);
        }
        if (row.size() > max(keyCol, valueCol)) {
            data[row[keyCol]] = row[valueCol];
        }
    }
    file.close();
}

// Function to load SOD (conflict) rules
void loadSODRules(const string& filename) {
    ifstream file(filename);
    if (!file.is_open()) {
        cerr << "❌ Error opening SOD Rules file: " << filename << endl;
        return;
    }

    string line;
    // Skip header line
    getline(file, line);
    
    while (getline(file, line)) {
        stringstream ss(line);
        string cell;
        vector<string> row;
        
        while (getline(ss, cell, ',')) {
            row.push_back(cell);
        }
        
        if (row.size() >= 5) {  // Ensure we have at least the first 5 columns
            string privilege1 = row[1];  // ENT_LEG1
            string privilege2 = row[2];  // ENT_LEG2
            
            // Skip empty privilege pairs
            if (privilege1 == "null" || privilege2 == "null" || privilege1.empty() || privilege2.empty()) {
                continue;
            }
            
            cout << "Loading SOD rule: " << privilege1 << " conflicts with " << privilege2 << endl;
            
            sodRules[privilege1].insert(privilege2);
            sodRules[privilege2].insert(privilege1); // Add reverse mapping
        }
    }
    file.close();
}

// Function to check for conflicts using SOD rules
void detectConflicts() {
    cout << "🔍 Starting conflict detection...\n";

    for (const auto& userRoles : userToRoles) {
        string user = userRoles.first;
        unordered_map<string, string> userPrivilegesWithRoles;  // Store privilege -> role mapping

        cout << "📌 Checking user: " << user << endl;

        for (const string& role : userRoles.second) {
            if (roleToPrivileges.find(role) != roleToPrivileges.end()) {
                cout << "    Role: " << role << endl;
                
                for (const string& privilege : roleToPrivileges[role]) {
                    cout << "        Privilege: " << privilege << endl;
                    
                    // Check against existing privileges for conflicts
                    for (const auto& existingEntry : userPrivilegesWithRoles) {
                        string existingPrivilege = existingEntry.first;
                        string existingRole = existingEntry.second;
                        
                        // Try exact match first
                        bool conflictFound = false;
                        if (sodRules.count(privilege) && sodRules[privilege].count(existingPrivilege)) {
                            conflictFound = true;
                        }
                        
                        // Try substring matching if no exact match
                        if (!conflictFound) {
                            for (const auto& rule : sodRules) {
                                // Check if the rule key is a substring of the privilege
                                if (privilege.find(rule.first) != string::npos) {
                                    for (const auto& conflictPriv : rule.second) {
                                        if (existingPrivilege.find(conflictPriv) != string::npos) {
                                            conflictFound = true;
                                            cout << "    🔍 Substring match: " << privilege << " contains " << rule.first 
                                                 << " and " << existingPrivilege << " contains " << conflictPriv << endl;
                                            break;
                                        }
                                    }
                                }
                                
                                if (conflictFound) break;
                            }
                        }
                        
                        if (conflictFound) {
                            string entity = privilegeToEntity.count(privilege) ? privilegeToEntity[privilege] : "Unknown";
                            conflicts.push_back({user, role, privilege, entity, "High-Risk"});
                            cout << "    🚨 Conflict! User: " << user << " has conflicting privileges: " 
                                 << privilege << " and " << existingPrivilege << endl;
                        }
                    }
                    
                    userPrivilegesWithRoles[privilege] = role;
                }
            }
        }
    }

    cout << "✅ Conflict detection completed.\n";
    cout << "📊 Total conflicts found: " << conflicts.size() << endl;
}

// Function to write results to CSV
void writeResultsToCSV(const string& outputFilename) {
    ofstream file(outputFilename);
    if (!file.is_open()) {
        cerr << "❌ Error creating output file: " << outputFilename << endl;
        return;
    }
    file << "User,Role,Privilege,Entity,Position\n";
    for (const auto& entry : conflicts) {
        file << entry.user << "," << entry.role << "," << entry.privilege << "," << entry.entity << "," << entry.position << "\n";
    }
    file.close();
    cout << "📂 Results written to " << outputFilename << endl;
}

void debugPrintMappings() {
    cout << "\n🔎 SOD Rules (Conflicting Privileges):\n";
    for (const auto& rule : sodRules) {
        cout << "  " << rule.first << " conflicts with: ";
        for (const auto& conflict : rule.second) {
            cout << conflict << ", ";
        }
        cout << endl;
    }
    
    cout << "\n📋 User to Roles Mapping:\n";
    for (const auto& user : userToRoles) {
        cout << "  User: " << user.first << " has roles: ";
        for (const auto& role : user.second) {
            cout << role << ", ";
        }
        cout << endl;
    }
    
    cout << "\n📋 Role to Privileges Mapping:\n";
    for (const auto& role : roleToPrivileges) {
        cout << "  Role: " << role.first << " has privileges: ";
        for (const auto& privilege : role.second) {
            cout << privilege << ", ";
        }
        cout << endl;
    }
}

int main() {
    cout << "🔄 Loading CSV data...\n";

    loadCSVData("XX_3_USER_ROLE_MAPPING_CONFLICTS_CLEAN.csv", userToRoles, 0, 1);
    loadCSVData("XX_6_PVLG_TO_ROLE_RELATION_CONFLICTS_CLEAN.csv", roleToPrivileges, 0, 1);
    loadCSVData("XX_7_PVLGS_MASTER_RPT_filtered (1).csv", privilegeToEntity, 0, 1);
    loadSODRules("SOD_Ruleset_EXPANDED.csv");
    cout << "\n📌 DEBUG: All Privilege-to-Entity Mappings\n";
    for (const auto& entry : privilegeToEntity) {
    cout << "Privilege: " << entry.first << " -> Entity: " << entry.second << endl;
    }
    cout << "\n📌 DEBUG: Privileges without entity mappings\n";
    for (const auto& entry : roleToPrivileges) {
        for (const string& privilege : entry.second) {
            if (privilegeToEntity.find(privilege) == privilegeToEntity.end()) {
                cout << "Missing: " << privilege << endl;
            }
        }
    }

    detectConflicts();
    writeResultsToCSV("conflict_results.csv");

    return 0;
}
