"""
Grade 10 Curriculum Data Seeding Script
Subjects: Geography, History and Citizenship, Kiswahili Lugha, Literature in English, Physics

This script seeds curriculum data from KICD curriculum designs into the MongoDB database.
It replaces existing data for these subjects to maintain data integrity.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime
import os

# MongoDB connection
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "cbeplanner-oregon"

# Connect to MongoDB
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# ============================================================================
# CURRICULUM DATA DEFINITIONS
# ============================================================================

# Get Grade 10 ID - will be fetched from database
GRADE_10_ID = None

# Core Competencies (will map to existing IDs)
COMPETENCIES = {
    "Communication and Collaboration": "Communication and Collaboration",
    "Critical Thinking and Problem Solving": "Critical Thinking and Problem Solving",
    "Creativity and Imagination": "Creativity and Imagination",
    "Digital Literacy": "Digital Literacy",
    "Learning to Learn": "Learning to Learn",
    "Self-Efficacy": "Self-Efficacy",
    "Citizenship": "Citizenship",
}

# Values (will map to existing IDs)
VALUES = {
    "Unity": "Unity",
    "Patriotism": "Patriotism",
    "Responsibility": "Responsibility",
    "Peace": "Peace",
    "Respect": "Respect",
    "Integrity": "Integrity",
    "Social Justice": "Social Justice",
    "Love": "Love",
}

# PCIs (will map to existing IDs)
PCIS = {
    "Environmental Education": "Environmental Education",
    "Safety and Security": "Safety and Security",
    "Social Cohesion": "Social Cohesion",
    "Financial Literacy": "Financial Literacy",
    "Health Education": "Health Education",
    "Citizenship Education": "Citizenship Education",
    "Life Skills": "Life Skills",
}

# ============================================================================
# GEOGRAPHY CURRICULUM DATA
# ============================================================================

GEOGRAPHY_DATA = {
    "name": "Geography",
    "strands": [
        {
            "name": "Practical Geography",
            "substrands": [
                {
                    "name": "Introduction to Geography",
                    "lessons": 8,
                    "slos": [
                        {
                            "name": "Analyse branches of Geography",
                            "description": "Analyse the branches of Geography for in-depth understanding of the subject",
                            "learning_activities": {
                                "introduction": "Brainstorm on the meaning and branches of Geography and make class presentations",
                                "development": "Use print or digital resources to establish the importance of studying Geography. Discuss the relationship between Geography and other disciplines",
                                "conclusion": "Engage with resource person on careers related to Geography and take notes",
                                "extended": "Create posters on careers related to Geography and display in school",
                                "resources": ["Approved textbooks", "Digital resources", "Library", "Display boards", "Photographs"],
                                "assessment": ["Oral Questions", "Written tests", "Observation", "Portfolios"]
                            },
                            "competencies": ["Communication and Collaboration", "Critical Thinking and Problem Solving", "Creativity and Imagination"],
                            "values": ["Unity", "Responsibility"],
                            "pcis": ["Self-Awareness", "Creative Thinking"],
                            "inquiry_questions": ["How does the study of Geography impact on peoples lives?"]
                        },
                        {
                            "name": "Examine importance of studying Geography",
                            "description": "Examine the importance of studying Geography for sustainable development",
                            "learning_activities": {
                                "introduction": "Discuss the significance of Geography in day-to-day life",
                                "development": "Conduct digital or library research on the significance of Geography",
                                "conclusion": "Make class presentations on findings",
                                "extended": "Engage in work shadowing on a possible career in Geography",
                                "resources": ["Approved textbooks", "Digital resources", "Library"],
                                "assessment": ["Oral Questions", "Written tests", "Portfolios"]
                            },
                            "competencies": ["Communication and Collaboration", "Critical Thinking and Problem Solving"],
                            "values": ["Unity", "Responsibility"],
                            "pcis": ["Self-Awareness"],
                            "inquiry_questions": ["How does the study of Geography impact on peoples lives?"]
                        }
                    ]
                },
                {
                    "name": "Map Reading and Interpretation",
                    "lessons": 13,
                    "slos": [
                        {
                            "name": "Illustrate methods of representing relief",
                            "description": "Illustrate the various methods of representing relief on topographical maps",
                            "learning_activities": {
                                "introduction": "Brainstorm on meaning and types of maps and share in class",
                                "development": "Use print or digital resources to research on methods of representing relief, drainage and vegetation on topographical maps. Draw sketches",
                                "conclusion": "Discuss how relief, drainage and vegetation are interpreted on topographical maps",
                                "extended": "Watch video clips on relief, drainage, and vegetation",
                                "resources": ["Topographical Maps", "Digital resources", "Photographs", "Pictures"],
                                "assessment": ["Oral Questions", "Written tests", "Observation", "Portfolios"]
                            },
                            "competencies": ["Self-Efficacy", "Digital Literacy", "Critical Thinking and Problem Solving"],
                            "values": ["Unity", "Respect", "Responsibility"],
                            "pcis": ["Self-Awareness", "Environmental Education"],
                            "inquiry_questions": ["How do we read and interpret topographical maps?"]
                        },
                        {
                            "name": "Interpret relief and drainage on maps",
                            "description": "Interpret relief, drainage and vegetation on topographical maps for resource mapping",
                            "learning_activities": {
                                "introduction": "Review types of maps",
                                "development": "Draw sketch sections from topographical maps. Use relief, drainage and vegetation to identify economic activities",
                                "conclusion": "Display sketches in class for peer review",
                                "extended": "Field visit to observe local landscape features",
                                "resources": ["Topographical Maps", "Digital resources", "Local environment"],
                                "assessment": ["Oral Questions", "Written tests", "Observation", "Checklists"]
                            },
                            "competencies": ["Self-Efficacy", "Digital Literacy", "Critical Thinking and Problem Solving"],
                            "values": ["Unity", "Respect", "Responsibility"],
                            "pcis": ["Environmental Education", "Online Safety"],
                            "inquiry_questions": ["How do we read and interpret topographical maps?"]
                        }
                    ]
                },
                {
                    "name": "Statistical Methods",
                    "lessons": 12,
                    "slos": [
                        {
                            "name": "Analyse importance of statistics",
                            "description": "Analyse the importance of statistics in Geography",
                            "learning_activities": {
                                "introduction": "Brainstorm on the importance of statistics in Geography",
                                "development": "Conduct library research on limitations of statistics. Role play methods of data collection",
                                "conclusion": "Discuss methods of data analysis and presentation",
                                "extended": "Carry out research within school on a selected geographical topic",
                                "resources": ["Digital resources", "Approved textbooks", "Charts", "Flipcharts"],
                                "assessment": ["Oral Questions", "Written tests", "Projects", "Portfolios"]
                            },
                            "competencies": ["Critical Thinking and Problem Solving", "Creativity and Imagination", "Learning to Learn"],
                            "values": ["Integrity", "Respect"],
                            "pcis": ["Critical Thinking", "Social Cohesion"],
                            "inquiry_questions": ["How do we use statistics in day-to-day life?"]
                        }
                    ]
                },
                {
                    "name": "Geographic Information Systems (GIS)",
                    "lessons": 13,
                    "slos": [
                        {
                            "name": "Explain GIS, GPS and Remote Sensing",
                            "description": "Explain Geographic Information Systems (GIS), Global Positioning System (GPS) and Remote Sensing (RS) as geospatial technologies",
                            "learning_activities": {
                                "introduction": "Brainstorm on GIS, GPS and RS as geospatial technologies",
                                "development": "Discuss components of GIS (data, software, hardware, users, methods). Research importance of GIS",
                                "conclusion": "Convert geographic coordinates and present in class",
                                "extended": "Use digital resources to locate points on earth's surface. Create posters on GIS importance",
                                "resources": ["Digital resources", "Maps", "Digitizers", "Approved textbooks"],
                                "assessment": ["Oral Questions", "Written tests", "Projects", "Portfolios"]
                            },
                            "competencies": ["Learning to Learn", "Digital Literacy"],
                            "values": ["Responsibility", "Respect"],
                            "pcis": ["Social Cohesion", "Critical Thinking", "Self-Awareness"],
                            "inquiry_questions": ["How is geospatial technology useful to humans?"]
                        }
                    ]
                }
            ]
        },
        {
            "name": "Natural Systems and Processes",
            "substrands": [
                {
                    "name": "Rocks",
                    "lessons": 18,
                    "slos": [
                        {
                            "name": "Examine classification of rocks",
                            "description": "Examine the classification of rocks according to the mode of formation and age",
                            "learning_activities": {
                                "introduction": "Brainstorm the meaning of rocks",
                                "development": "Use print or digital resources to establish classification of rocks. Discuss characteristics of igneous, metamorphic and sedimentary rocks",
                                "conclusion": "Draw sketch map of Kenya showing distribution of rocks",
                                "extended": "Carry out field study on rocks within local environment. Make a collage showing distribution of rocks",
                                "resources": ["Photographs", "Maps", "Rock samples", "Digital resources", "Museums"],
                                "assessment": ["Oral Questions", "Written tests", "Projects", "Field reports"]
                            },
                            "competencies": ["Creativity and Imagination", "Learning to Learn", "Citizenship"],
                            "values": ["Patriotism", "Unity"],
                            "pcis": ["Environmental Education", "Safety", "First Aid"],
                            "inquiry_questions": ["Why are there different types of rocks?"]
                        }
                    ]
                },
                {
                    "name": "Folding",
                    "lessons": 12,
                    "slos": [
                        {
                            "name": "Distinguish types of folds",
                            "description": "Distinguish the types of folds resulting from tectonic forces",
                            "learning_activities": {
                                "introduction": "Brainstorm on the meaning of folding",
                                "development": "Discuss types of folds resulting from tectonic forces. Research resultant features of folding",
                                "conclusion": "Draw sketches of resultant features. Model resultant features",
                                "extended": "Draw world map showing distribution of fold mountains. Debate on significance of folding",
                                "resources": ["Photographs", "Maps", "Digital resources", "Models", "Plasticine"],
                                "assessment": ["Oral Questions", "Written tests", "Projects", "Portfolios"]
                            },
                            "competencies": ["Citizenship", "Creativity and Imagination"],
                            "values": ["Unity", "Respect"],
                            "pcis": ["Environmental Education", "Creativity", "Assertiveness"],
                            "inquiry_questions": ["How does folding influence our day-to-day life?"]
                        }
                    ]
                },
                {
                    "name": "Vulcanicity",
                    "lessons": 13,
                    "slos": [
                        {
                            "name": "Investigate causes of vulcanicity",
                            "description": "Investigate the causes of vulcanicity in the Earth",
                            "learning_activities": {
                                "introduction": "Brainstorm on meaning and causes of vulcanicity",
                                "development": "Research features resulting from vulcanicity. Draw intrusive features. Model extrusive features",
                                "conclusion": "Watch video clips on volcanic activities. Simulate volcanic eruptions",
                                "extended": "Create posters of volcanic features. Make collage on distribution of volcanic features in Kenya",
                                "resources": ["Photographs", "Maps", "Resource persons", "Paper Mache", "Digital resources"],
                                "assessment": ["Oral Questions", "Written tests", "Projects", "Portfolios"]
                            },
                            "competencies": ["Self-Efficacy", "Learning to Learn", "Digital Literacy"],
                            "values": ["Peace", "Integrity"],
                            "pcis": ["Environmental Education", "Creative Thinking"],
                            "inquiry_questions": ["Why study vulcanicity?"]
                        }
                    ]
                },
                {
                    "name": "Earthquakes",
                    "lessons": 10,
                    "slos": [
                        {
                            "name": "Examine causes of earthquakes",
                            "description": "Examine causes of earthquakes on Earth",
                            "learning_activities": {
                                "introduction": "Brainstorm on meaning, types and causes of earthquakes",
                                "development": "Draw world map showing earthquake zones. Discuss measurement scales (Richter and Mercalli)",
                                "conclusion": "Watch video clips on effects of earthquakes. Engage resource person on disaster preparedness",
                                "extended": "Make communication messages on disaster preparedness and management",
                                "resources": ["Photographs", "Maps", "Resource persons", "Digital resources"],
                                "assessment": ["Oral Questions", "Written tests", "Projects", "Portfolios"]
                            },
                            "competencies": ["Digital Literacy", "Creativity and Imagination"],
                            "values": ["Unity", "Respect"],
                            "pcis": ["Environmental Education", "Self-Esteem"],
                            "inquiry_questions": ["Why are earthquakes of concern to humans?"]
                        }
                    ]
                }
            ]
        },
        {
            "name": "Human and Economic Activities",
            "substrands": [
                {
                    "name": "Agriculture",
                    "lessons": 15,
                    "slos": [
                        {
                            "name": "Explore types of agriculture",
                            "description": "Explore types of agriculture in the world (subsistence, commercial, urban agriculture)",
                            "learning_activities": {
                                "introduction": "Brainstorm on types of agriculture in the world",
                                "development": "Engage resource person on importance of agriculture. Research trends in agriculture in Africa",
                                "conclusion": "Watch video clips on urban agriculture and hydroponics",
                                "extended": "Conduct field study on strategies for enhancing agricultural productivity. Create posters",
                                "resources": ["Photographs", "Model farms", "Local environments", "Digital resources"],
                                "assessment": ["Oral Questions", "Written tests", "Projects"]
                            },
                            "competencies": ["Learning to Learn", "Citizenship"],
                            "values": ["Social Justice", "Patriotism"],
                            "pcis": ["Social Cohesion", "Assertiveness"],
                            "inquiry_questions": ["How is the future of agriculture in Kenya?"]
                        }
                    ]
                },
                {
                    "name": "Mining",
                    "lessons": 20,
                    "slos": [
                        {
                            "name": "Examine factors influencing mining",
                            "description": "Examine the factors influencing occurrence and exploitation of minerals",
                            "learning_activities": {
                                "introduction": "Brainstorm on meaning of minerals and mining",
                                "development": "Research occurrence of minerals. Discuss methods of extraction. Watch documentaries on mining",
                                "conclusion": "Write article on effects of mining on environment",
                                "extended": "Create communication messages on importance of rehabilitating mining sites",
                                "resources": ["Photographs", "Maps", "Digital resources", "Approved textbooks"],
                                "assessment": ["Oral Questions", "Written tests", "Projects", "Portfolios"]
                            },
                            "competencies": ["Citizenship", "Digital Literacy", "Communication and Collaboration"],
                            "values": ["Unity", "Respect"],
                            "pcis": ["Self-Awareness", "Environmental Education"],
                            "inquiry_questions": ["How can we exploit minerals sustainably?"]
                        }
                    ]
                },
                {
                    "name": "Energy",
                    "lessons": 20,
                    "slos": [
                        {
                            "name": "Examine types and sources of energy",
                            "description": "Examine the types and sources of energy for domestic and industrial use",
                            "learning_activities": {
                                "introduction": "Brainstorm on meaning of energy",
                                "development": "Research types and sources of energy. Watch video clips on renewable energy development",
                                "conclusion": "Discuss development of renewable energy in Kenya and selected countries",
                                "extended": "Develop communication messages on energy conservation. Make energy-saving devices",
                                "resources": ["Photographs", "Maps", "Digital resources", "Approved textbooks"],
                                "assessment": ["Oral Questions", "Written tests", "Projects", "Portfolios"]
                            },
                            "competencies": ["Critical Thinking and Problem Solving", "Learning to Learn", "Citizenship"],
                            "values": ["Unity", "Responsibility"],
                            "pcis": ["Financial Literacy", "Environmental Education", "Safety and Security"],
                            "inquiry_questions": ["Why renewable energy?"]
                        }
                    ]
                },
                {
                    "name": "Industry",
                    "lessons": 20,
                    "slos": [
                        {
                            "name": "Explore types of industries",
                            "description": "Explore the types of industries in the world",
                            "learning_activities": {
                                "introduction": "Brainstorm on industry and industrialization",
                                "development": "Discuss types of industries. Research factors influencing location of industries",
                                "conclusion": "Draw map of Kenya showing major industries. Debate on significance of industries",
                                "extended": "Watch video clips on Jua Kali industries. Model a cottage industry in school",
                                "resources": ["Photographs", "Maps", "Digital resources", "Approved textbooks"],
                                "assessment": ["Oral Questions", "Written tests", "Projects", "Portfolios"]
                            },
                            "competencies": ["Critical Thinking and Problem Solving", "Creativity and Imagination"],
                            "values": ["Social Justice", "Patriotism"],
                            "pcis": ["Financial Literacy", "Consumer Education"],
                            "inquiry_questions": ["What is the status and prospects of industrialization in Kenya?"]
                        }
                    ]
                }
            ]
        }
    ]
}

# ============================================================================
# HISTORY AND CITIZENSHIP CURRICULUM DATA
# ============================================================================

HISTORY_CITIZENSHIP_DATA = {
    "name": "History and Citizenship",
    "strands": [
        {
            "name": "Themes in Kenyan History and Citizenship",
            "substrands": [
                {
                    "name": "Linguistic groups in Kenya",
                    "lessons": 10,
                    "slos": [
                        {
                            "name": "Explore linguistic groups in Kenya",
                            "description": "Explore the linguistic groups in Kenya and discuss causes and effects of migration, settlement and expansion",
                            "learning_activities": {
                                "introduction": "Brainstorm on identities of linguistic groups in Kenya",
                                "development": "Discuss and write on charts the linguistic groups. Investigate causes and effects of migration",
                                "conclusion": "Using atlas, draw map of Kenya and locate migration routes and settlement areas",
                                "extended": "Role play cultural exchange. Compose song or poem on cultural diversity",
                                "resources": ["Approved textbooks", "Digital resources", "Library", "Display boards", "UNESCO-General History of Africa"],
                                "assessment": ["Oral Questions", "Written tests", "Observation", "Rubrics", "Portfolio"]
                            },
                            "competencies": ["Communication and Collaboration", "Citizenship"],
                            "values": ["Responsibility", "Unity"],
                            "pcis": ["Citizenship Education", "Ethnic relations"],
                            "inquiry_questions": ["How can you promote harmonious living among diverse communities of Kenya?"]
                        }
                    ]
                },
                {
                    "name": "Establishment of colonial rule",
                    "lessons": 12,
                    "slos": [
                        {
                            "name": "Examine reasons for colonial rule",
                            "description": "Examine the reasons for the establishment of colonial rule and methods applied by the British",
                            "learning_activities": {
                                "introduction": "Use digital devices or print materials to research reasons for colonial rule",
                                "development": "Roleplay methods used by British. Watch documentary on establishment of colonial rule",
                                "conclusion": "Develop chart on process of establishment of colonial rule",
                                "extended": "Develop communication messages on independence and unity",
                                "resources": ["Approved textbooks", "Digital resources", "Library", "Charts", "Resource person"],
                                "assessment": ["Oral Questions", "Written tests", "Observation", "Portfolio", "Rubrics"]
                            },
                            "competencies": ["Digital Literacy", "Self-Efficacy"],
                            "values": ["Unity", "Responsibility"],
                            "pcis": ["Safety and Security", "Online Safety"],
                            "inquiry_questions": ["How can we maintain independence in daily lives?", "Why was it wrong for British to impose rule on Africans?"]
                        }
                    ]
                },
                {
                    "name": "The Constitution of Kenya (2010)",
                    "lessons": 8,
                    "slos": [
                        {
                            "name": "Analyse public resources in Kenya",
                            "description": "Categorise types of public resources in Kenya and analyse their importance for posterity",
                            "learning_activities": {
                                "introduction": "Identify and categorise types of public resources",
                                "development": "Watch video clip on importance of efficient use of public resources. Engage resource person",
                                "conclusion": "Conduct debate on advocacy for efficient use of public resources",
                                "extended": "Design charts/posters/songs to support efficient use of public resources",
                                "resources": ["Digital resources", "Approved textbooks", "Library", "Charts", "Resource person"],
                                "assessment": ["Oral Questions", "Written tests", "Observation", "Portfolio", "Rubrics"]
                            },
                            "competencies": ["Communication and Collaboration", "Learning to Learn"],
                            "values": ["Patriotism", "Responsibility"],
                            "pcis": ["Citizenship Education", "Civic responsibility"],
                            "inquiry_questions": ["What are challenges in ensuring efficient utilisation of public resources?"]
                        }
                    ]
                },
                {
                    "name": "Political developments since independence",
                    "lessons": 10,
                    "slos": [
                        {
                            "name": "Analyse political developments in Kenya",
                            "description": "Analyse major political developments in Kenya since Independence and discuss challenges",
                            "learning_activities": {
                                "introduction": "Use digital or print resources to establish major political developments",
                                "development": "Engage resource person on major political challenges. Hold discussions on solutions",
                                "conclusion": "Participate in activities to promote conducive political environment",
                                "extended": "Compose and sing song on importance of harmonious living",
                                "resources": ["Digital resources", "Approved textbooks", "Library", "Charts", "Resource person"],
                                "assessment": ["Oral Questions", "Written tests", "Observation", "Portfolio", "Rubrics"]
                            },
                            "competencies": ["Critical Thinking and Problem Solving", "Citizenship"],
                            "values": ["Patriotism", "Social Justice"],
                            "pcis": ["Citizenship Education", "National values"],
                            "inquiry_questions": ["How can you participate in political developments in your community?"]
                        }
                    ]
                },
                {
                    "name": "Elections in Kenya",
                    "lessons": 15,
                    "slos": [
                        {
                            "name": "Identify guidelines governing elections",
                            "description": "Identify guidelines governing elections in Kenya and describe roles of IEBC",
                            "learning_activities": {
                                "introduction": "Use print and non-print materials to search for guidelines governing elections",
                                "development": "Brainstorm on roles and functions of IEBC. Use charts/posters to enumerate roles",
                                "conclusion": "Role play electoral processes in school",
                                "extended": "Engage resource person on measures to curb election malpractices",
                                "resources": ["Digital resources", "Approved textbooks", "Library", "Charts", "Resource person"],
                                "assessment": ["Oral Questions", "Written tests", "Observation", "Portfolio", "Rubrics"]
                            },
                            "competencies": ["Citizenship", "Creativity and Imagination"],
                            "values": ["Unity", "Social Justice"],
                            "pcis": ["Citizenship Education", "Good governance", "Social cohesion"],
                            "inquiry_questions": ["Why are elections important?", "Which values can citizens embrace to avoid election malpractices?"]
                        }
                    ]
                },
                {
                    "name": "National integration",
                    "lessons": 8,
                    "slos": [
                        {
                            "name": "Discuss importance of national integration",
                            "description": "Discuss importance of national integration and explain components that enhance it",
                            "learning_activities": {
                                "introduction": "Brainstorm on importance of national integration",
                                "development": "Use digital or print resources to find components of national integration. Research limiting factors",
                                "conclusion": "Identify and participate in ways that enhance national integration",
                                "extended": "Develop communication messages for promotion of peaceful co-existence",
                                "resources": ["Digital resources", "Approved textbooks", "Library", "Charts", "Resource person"],
                                "assessment": ["Oral Questions", "Written tests", "Observation", "Portfolio", "Rubrics"]
                            },
                            "competencies": ["Communication and Collaboration", "Digital Literacy"],
                            "values": ["Patriotism", "Unity"],
                            "pcis": ["Citizenship Education", "Good governance", "Ethnic relations"],
                            "inquiry_questions": ["How can you enhance national integration?"]
                        }
                    ]
                }
            ]
        },
        {
            "name": "Themes in African History and Citizenship",
            "substrands": [
                {
                    "name": "Human Developments in Africa",
                    "lessons": 10,
                    "slos": [
                        {
                            "name": "Explain transition to sedentary lifestyle",
                            "description": "Explain factors that led to transition from migratory to sedentary lifestyle by early humans",
                            "learning_activities": {
                                "introduction": "Use digital/print materials to identify factors for transition",
                                "development": "Brainstorm meaning of Neolithic revolution. Discuss advancements during Neolithic period",
                                "conclusion": "Investigate characteristics of pastoralism in Maasai and Fulani communities",
                                "extended": "Design charts/posters on solutions to challenges facing contemporary pastoralism",
                                "resources": ["Maps", "Digital resources", "Museums", "Artefacts", "Fossils", "UNESCO-General History of Africa"],
                                "assessment": ["Oral Questions", "Written tests", "Project work", "Portfolio", "Rubrics"]
                            },
                            "competencies": ["Digital Literacy", "Critical Thinking and Problem Solving", "Learning to Learn"],
                            "values": ["Responsibility", "Patriotism"],
                            "pcis": ["Environmental conservation", "Online safety"],
                            "inquiry_questions": ["How did daily life change due to shifting from nomadic to sedentary life?"]
                        }
                    ]
                },
                {
                    "name": "African Civilizations up to 19th Century",
                    "lessons": 10,
                    "slos": [
                        {
                            "name": "Examine early African civilizations",
                            "description": "Examine development of selected early civilizations in Africa (Wanga, Buganda, Nyamwezi)",
                            "learning_activities": {
                                "introduction": "Brainstorm on development of selected early civilizations",
                                "development": "Discuss contributions of early civilizations to modern society using charts",
                                "conclusion": "Participate in activities that promote best practices in society",
                                "extended": "Document contributions in journal/school magazine",
                                "resources": ["Digital resources", "Map of Africa", "Museums", "Artefacts", "UNESCO-General History of Africa"],
                                "assessment": ["Oral Questions", "Written tests", "Project work", "Portfolio", "Rubrics"]
                            },
                            "competencies": ["Citizenship", "Learning to Learn"],
                            "values": ["Respect", "Unity"],
                            "pcis": ["Good Governance"],
                            "inquiry_questions": ["How do early civilizations differ from current leadership structure?"]
                        }
                    ]
                },
                {
                    "name": "Colonization of Africa",
                    "lessons": 10,
                    "slos": [
                        {
                            "name": "Discuss significance of Berlin Conference",
                            "description": "Discuss significance of Berlin Conference in relation to scramble for and partition of Africa",
                            "learning_activities": {
                                "introduction": "Research significance of Berlin Conference",
                                "development": "Engage resource person on key players in colonization. Establish extent of economic and political reasons",
                                "conclusion": "Debate on justification for end of colonialism",
                                "extended": "Compose poems/messages on justification to end colonization",
                                "resources": ["Digital resources", "Maps", "Audio visual", "Approved textbooks", "Resource person"],
                                "assessment": ["Oral Questions", "Written tests", "Project work", "Portfolio", "Rubrics"]
                            },
                            "competencies": ["Critical Thinking and Problem Solving", "Communication and Collaboration"],
                            "values": ["Social Justice", "Unity"],
                            "pcis": ["Citizenship Education", "Equity and non-discrimination"],
                            "inquiry_questions": ["How did Otto Von Bismarck fast-track scramble for Africa?", "Why was colonialism unfair to Africans?"]
                        }
                    ]
                },
                {
                    "name": "Modern Nationalism in Africa",
                    "lessons": 10,
                    "slos": [
                        {
                            "name": "Explore factors influencing nationalism",
                            "description": "Explore factors that have influenced nationalism in Africa and draw lessons from key leaders",
                            "learning_activities": {
                                "introduction": "Use digital/printed media to establish factors contributing to modern nationalism",
                                "development": "Discuss lessons from key leaders (Thomas Sankara, Desmond Tutu, Julius Nyerere, Anwar Sadat)",
                                "conclusion": "Engage resource person on best practices adopted by African nations",
                                "extended": "Document/prepare video on best practices on modern nationalism",
                                "resources": ["Digital resources", "Maps", "Audio visual", "Approved textbooks", "Resource person"],
                                "assessment": ["Oral Questions", "Written tests", "Project work", "Portfolio", "Rubrics"]
                            },
                            "competencies": ["Learning to Learn", "Digital Literacy"],
                            "values": ["Patriotism", "Unity"],
                            "pcis": ["Safety and Security", "Non-violent conflict resolution", "Ethnic relations"],
                            "inquiry_questions": ["How can you advance modern nationalism?"]
                        }
                    ]
                },
                {
                    "name": "Effects of global wars on Africa",
                    "lessons": 8,
                    "slos": [
                        {
                            "name": "Explore effects of global wars on Africa",
                            "description": "Explore how global wars affected Africa and apply lessons learnt for posterity",
                            "learning_activities": {
                                "introduction": "Brainstorm examples of global wars",
                                "development": "Research effects of World Wars, Cold War, Gulf War, Russia-Ukraine conflict on Africa",
                                "conclusion": "Share experiences on strategies of avoiding negative lessons from global wars",
                                "extended": "Compose songs/poems on discouraging global wars for sustainable peace",
                                "resources": ["Digital resources", "Maps", "Audio visual", "Approved textbooks", "Resource person"],
                                "assessment": ["Oral Questions", "Written tests", "Project work", "Portfolio", "Rubrics"]
                            },
                            "competencies": ["Learning to Learn", "Citizenship"],
                            "values": ["Peace", "Love"],
                            "pcis": ["Citizenship Education", "Peace Education"],
                            "inquiry_questions": ["Which strategies can UN apply to discourage global wars?"]
                        }
                    ]
                }
            ]
        },
        {
            "name": "International Themes in History and Citizenship",
            "substrands": [
                {
                    "name": "Great revolutions - French",
                    "lessons": 8,
                    "slos": [
                        {
                            "name": "Classify causes of French Revolution",
                            "description": "Classify causes of French Revolution and explain its significance to world economies",
                            "learning_activities": {
                                "introduction": "Brainstorm on classification of causes of French Revolution",
                                "development": "Use library resources to find significance of French Revolution",
                                "conclusion": "Investigate best practices from French Revolution",
                                "extended": "Write essay on significance of French Revolution in society today",
                                "resources": ["Charts", "Maps", "Museums", "UNESCO-General History of Africa"],
                                "assessment": ["Oral Questions", "Written tests", "Project work", "Rubrics", "Portfolio"]
                            },
                            "competencies": ["Learning to Learn", "Citizenship"],
                            "values": ["Social Justice", "Responsibility"],
                            "pcis": ["Citizenship Education", "Equity and non-discrimination"],
                            "inquiry_questions": ["What lessons do we learn from the French Revolution?"]
                        }
                    ]
                },
                {
                    "name": "International organisations",
                    "lessons": 8,
                    "slos": [
                        {
                            "name": "Enumerate significance of international organisations",
                            "description": "Enumerate significance of different types of international organisations and examine factors strengthening ties among Commonwealth countries",
                            "learning_activities": {
                                "introduction": "Brainstorm significance of different types of international organisations",
                                "development": "Discuss factors strengthening ties among Commonwealth countries using charts",
                                "conclusion": "Research opportunities and challenges facing Commonwealth nations",
                                "extended": "Create messages on significance of international organisations",
                                "resources": ["Approved textbooks", "UNESCO-General History of Africa"],
                                "assessment": ["Oral Questions", "Written tests", "Project work", "Rubrics", "Portfolio"]
                            },
                            "competencies": ["Learning to Learn", "Critical Thinking and Problem Solving"],
                            "values": ["Unity", "Respect"],
                            "pcis": ["Citizenship Education", "Social cohesion"],
                            "inquiry_questions": ["Why are key values important for sustainable relations among Commonwealth nations?"]
                        }
                    ]
                },
                {
                    "name": "Modern Slavery and Servitude",
                    "lessons": 10,
                    "slos": [
                        {
                            "name": "Discuss forms of modern slavery",
                            "description": "Discuss various forms of slavery and servitude in modern world and assess causative factors",
                            "learning_activities": {
                                "introduction": "Brainstorm difference between slavery and servitude",
                                "development": "Research forms of slavery and servitude. Discuss factors causing slavery in modern world",
                                "conclusion": "Engage resource person on how governments and civil society collaborate to end slavery",
                                "extended": "Compose song/poem on need to free world from slavery",
                                "resources": ["Realia", "Chart", "Audio visual", "Maps", "Digital resources", "Approved textbooks"],
                                "assessment": ["Oral Questions", "Written tests", "Project work", "Rubrics", "Portfolio"]
                            },
                            "competencies": ["Critical Thinking and Problem Solving", "Self-Efficacy"],
                            "values": ["Respect"],
                            "pcis": ["Social awareness skills"],
                            "inquiry_questions": ["What can you do to end slavery and servitude in the world?"]
                        }
                    ]
                },
                {
                    "name": "Global Governance",
                    "lessons": 10,
                    "slos": [
                        {
                            "name": "Identify guiding principles for global governance",
                            "description": "Identify guiding principles for global governance and illustrate key areas guaranteeing stable global trends",
                            "learning_activities": {
                                "introduction": "Role play guiding principles of global governance",
                                "development": "Prepare slogans on key areas in global governance. Research importance of global governance",
                                "conclusion": "Engage resource person on emerging issues and opportunities",
                                "extended": "Compose poem on importance of good global governance",
                                "resources": ["Chart", "Audio visual", "Maps", "Digital resources"],
                                "assessment": ["Oral Questions", "Written tests", "Observation", "Rubrics"]
                            },
                            "competencies": ["Communication and Collaboration", "Learning to Learn"],
                            "values": ["Responsibility", "Respect"],
                            "pcis": ["Citizenship Education", "Good governance", "Prevention of global warming"],
                            "inquiry_questions": ["Which activities are significant in promoting global governance?", "What is role of UN in fostering global governance?"]
                        }
                    ]
                },
                {
                    "name": "The 1st Industrial Revolution",
                    "lessons": 8,
                    "slos": [
                        {
                            "name": "Compare factors for industrial revolution",
                            "description": "Compare factors that led to industrial revolution in Britain and USA and discuss impacts on Africa",
                            "learning_activities": {
                                "introduction": "Brainstorm characteristics of industrial revolution",
                                "development": "Discuss factors that led to 1st industrial revolution in Britain and USA. Research impacts on Africa",
                                "conclusion": "Watch video clip on measures taken to address impacts",
                                "extended": "Compose songs/poems/messages on measures to address impacts",
                                "resources": ["Approved textbooks", "Posters", "UNESCO-General History of Africa", "Chart", "Digital resources"],
                                "assessment": ["Oral Questions", "Written tests", "Observation", "Rubrics"]
                            },
                            "competencies": ["Self-Efficacy", "Creativity and Imagination"],
                            "values": ["Responsibility", "Unity"],
                            "pcis": ["Citizenship Education", "Equity and non-discrimination"],
                            "inquiry_questions": ["How did 1st industrial revolution underdevelop Africa?", "How did it contribute to colonization?"]
                        }
                    ]
                }
            ]
        },
        {
            "name": "Contemporary Themes in History and Citizenship",
            "substrands": [
                {
                    "name": "Peace and Conflict transformations in Kenya",
                    "lessons": 8,
                    "slos": [
                        {
                            "name": "Identify activities contributing to peace",
                            "description": "Identify national activities that contribute to peace in Kenya for harmonious living",
                            "learning_activities": {
                                "introduction": "Hold discussion on national activities used to promote peace",
                                "development": "Engage resource person on ways Constitution (2010) strives to prevent conflicts",
                                "conclusion": "Research incidences where constitution has been applied to foster peace",
                                "extended": "Role play how to uphold peace and curb conflicts in different situations",
                                "resources": ["Approved textbooks", "Online sources", "Library", "Charts", "Constitution of Kenya"],
                                "assessment": ["Rubrics", "Written tests", "Oral assessment", "Observation", "Portfolio"]
                            },
                            "competencies": ["Critical Thinking and Problem Solving", "Communication and Collaboration"],
                            "values": ["Responsibility", "Respect"],
                            "pcis": ["Citizenship Education", "Peace Education"],
                            "inquiry_questions": ["What are benefits of a peaceful nation?", "How do you promote peace and conflict transformation?"]
                        }
                    ]
                },
                {
                    "name": "The 4th Industrial and Technologies Revolution",
                    "lessons": 9,
                    "slos": [
                        {
                            "name": "Trace technological advancements in 4th generation",
                            "description": "Trace technological advancements in 4th generation and analyse role of ICT",
                            "learning_activities": {
                                "introduction": "Use digital or print resources to trace technological advancements",
                                "development": "Engage resource person on role of ICT in 4th Industrial Revolution",
                                "conclusion": "Debate on impact of technology in 4th Industrial Revolution in Africa",
                                "extended": "Create online platform for communication within school community. Create gallery showcasing advancements",
                                "resources": ["Digital devices", "Reference materials", "Constitution of Kenya", "Resource person"],
                                "assessment": ["Rubrics", "Written tests", "Oral assessment", "Observation", "Portfolio"]
                            },
                            "competencies": ["Critical Thinking and Problem Solving", "Digital Literacy"],
                            "values": ["Respect", "Integrity"],
                            "pcis": ["Safety and Security", "Online Safety", "Financial Literacy"],
                            "inquiry_questions": ["What are benefits of 4th generation technologies?", "How has technology revolutionized acquisition of historical information?"]
                        }
                    ]
                },
                {
                    "name": "Equity and non-discrimination",
                    "lessons": 8,
                    "slos": [
                        {
                            "name": "Analyse factors promoting equity",
                            "description": "Analyse factors that promote equity and non-discrimination in society",
                            "learning_activities": {
                                "introduction": "Discuss factors that promote equity and non-discrimination",
                                "development": "Research historical injustice that promote inequality and discrimination",
                                "conclusion": "Use flashcards/charts to develop measures that promote equity",
                                "extended": "Participate in activities that curb inequity and discrimination",
                                "resources": ["Approved textbooks", "Constitution of Kenya", "Online sources", "Library", "Charts"],
                                "assessment": ["Rubrics", "Written tests", "Observation", "Checklist", "Portfolio"]
                            },
                            "competencies": ["Critical Thinking and Problem Solving", "Communication and Collaboration"],
                            "values": ["Respect", "Unity"],
                            "pcis": ["Online Safety", "Citizenship Education", "Social cohesion"],
                            "inquiry_questions": ["How can we eradicate inequality and discrimination in society?"]
                        }
                    ]
                }
            ]
        }
    ]
}

# ============================================================================
# KISWAHILI LUGHA CURRICULUM DATA
# ============================================================================

KISWAHILI_LUGHA_DATA = {
    "name": "Kiswahili Lugha",
    "strands": [
        {
            "name": "Kusikiliza na Kuzungumza (Listening and Speaking)",
            "substrands": [
                {
                    "name": "Usikilizaji Husishi (Active Listening)",
                    "lessons": 8,
                    "slos": [
                        {
                            "name": "Kueleza maana ya usikilizaji husishi",
                            "description": "Explain meaning of active listening and discuss its importance in communication",
                            "learning_activities": {
                                "introduction": "Explain meaning of active listening",
                                "development": "Discuss importance of active listening. Read about contexts of active listening",
                                "conclusion": "Discuss principles of active listening (valuing speaker's opinions, maintaining eye contact, avoiding distractions)",
                                "extended": "Participate in active listening exercises with peers. Role play conversations",
                                "resources": ["Books", "Digital devices", "Audio recorders", "Charts", "Guest speakers"],
                                "assessment": ["Observation", "Oral presentations", "Listening comprehension tests", "Peer assessment"]
                            },
                            "competencies": ["Communication and Collaboration", "Digital Literacy", "Critical Thinking and Problem Solving", "Self-Efficacy"],
                            "values": ["Unity", "Respect", "Responsibility"],
                            "pcis": ["Self-Awareness", "Social Cohesion"],
                            "inquiry_questions": ["What is importance of active listening?", "What techniques ensure successful active listening?"]
                        }
                    ]
                },
                {
                    "name": "Kuhakiki Matini (Critical Listening)",
                    "lessons": 6,
                    "slos": [
                        {
                            "name": "Kusikiliza kwa kupambanua",
                            "description": "Listen critically to distinguish elements in spoken texts and evaluate information",
                            "learning_activities": {
                                "introduction": "Discuss critical listening and its characteristics",
                                "development": "Listen to audio/video clips and analyze content critically",
                                "conclusion": "Present critical analysis of listened materials",
                                "extended": "Practice evaluating news, speeches, and discussions",
                                "resources": ["Audio recordings", "Video clips", "Digital devices", "Charts"],
                                "assessment": ["Listening tests", "Critical analysis reports", "Oral presentations"]
                            },
                            "competencies": ["Critical Thinking and Problem Solving", "Communication and Collaboration"],
                            "values": ["Integrity", "Respect"],
                            "pcis": ["Media Literacy", "Critical Thinking"],
                            "inquiry_questions": ["How do we evaluate spoken information critically?"]
                        }
                    ]
                }
            ]
        },
        {
            "name": "Kusoma (Reading)",
            "substrands": [
                {
                    "name": "Kusoma kwa Kina (Intensive Reading)",
                    "lessons": 8,
                    "slos": [
                        {
                            "name": "Kueleza mbinu ya kuduhushi",
                            "description": "Explain skimming and scanning techniques in reading to obtain specific information",
                            "learning_activities": {
                                "introduction": "Explain meaning of intensive reading techniques (skimming, scanning)",
                                "development": "Discuss relationship and differences between skimming and scanning. Practice techniques",
                                "conclusion": "Read texts using intensive reading techniques focusing on vocabulary and language use",
                                "extended": "Research additional texts online and apply intensive reading techniques",
                                "resources": ["Textbooks", "Digital devices", "Internet access", "Notebooks"],
                                "assessment": ["Reading comprehension exercises", "Analysis of summaries", "Observation"]
                            },
                            "competencies": ["Communication and Collaboration", "Critical Thinking and Problem Solving", "Digital Literacy"],
                            "values": ["Responsibility", "Respect"],
                            "pcis": ["Academic Skills", "Research Skills"],
                            "inquiry_questions": ["What is importance of intensive reading techniques?"]
                        }
                    ]
                },
                {
                    "name": "Kusoma kwa Mapana (Extensive Reading)",
                    "lessons": 6,
                    "slos": [
                        {
                            "name": "Kusoma matini mbalimbali",
                            "description": "Read various texts for pleasure and general understanding",
                            "learning_activities": {
                                "introduction": "Discuss importance of reading for pleasure",
                                "development": "Select and read books of personal interest. Discuss themes and content",
                                "conclusion": "Present book reviews to classmates",
                                "extended": "Maintain reading journal documenting books read",
                                "resources": ["Library books", "Magazines", "Newspapers", "Digital resources"],
                                "assessment": ["Book reviews", "Reading journals", "Oral presentations"]
                            },
                            "competencies": ["Learning to Learn", "Communication and Collaboration"],
                            "values": ["Responsibility", "Love"],
                            "pcis": ["Life-long Learning", "Cultural Appreciation"],
                            "inquiry_questions": ["How does extensive reading improve language skills?"]
                        }
                    ]
                }
            ]
        },
        {
            "name": "Kuandika (Writing)",
            "substrands": [
                {
                    "name": "Tafsiri (Translation)",
                    "lessons": 10,
                    "slos": [
                        {
                            "name": "Kueleza maana ya tafsiri",
                            "description": "Explain meaning of translation and its importance in communication",
                            "learning_activities": {
                                "introduction": "Explain meaning of translation",
                                "development": "Discuss types of translation (word for word, semantic, communicative). Explain importance of translation",
                                "conclusion": "Research elements to consider in translation. Discuss steps in translation process",
                                "extended": "Practice translating texts at appropriate level following proper procedures",
                                "resources": ["Textbooks", "Dictionaries", "Internet resources", "Translation software"],
                                "assessment": ["Translation exercises", "Analysis of translated work", "Peer review"]
                            },
                            "competencies": ["Communication and Collaboration", "Creativity and Imagination", "Self-Efficacy"],
                            "values": ["Respect", "Responsibility", "Integrity"],
                            "pcis": ["Intercultural Communication", "Language Development"],
                            "inquiry_questions": ["What is importance of translation in communication?", "What elements do you consider when translating?"]
                        }
                    ]
                },
                {
                    "name": "Insha Fafanuzi (Expository Essay)",
                    "lessons": 8,
                    "slos": [
                        {
                            "name": "Kuandika insha fafanuzi",
                            "description": "Write expository essays explaining various topics",
                            "learning_activities": {
                                "introduction": "Discuss characteristics of expository essays",
                                "development": "Analyze sample expository essays. Plan and outline topics",
                                "conclusion": "Write expository essays on given topics",
                                "extended": "Peer review and edit essays for improvement",
                                "resources": ["Textbooks", "Sample essays", "Writing guides"],
                                "assessment": ["Essay evaluation", "Peer review", "Teacher feedback"]
                            },
                            "competencies": ["Communication and Collaboration", "Critical Thinking and Problem Solving"],
                            "values": ["Integrity", "Responsibility"],
                            "pcis": ["Academic Writing", "Clear Communication"],
                            "inquiry_questions": ["How do we write effective expository essays?"]
                        }
                    ]
                }
            ]
        },
        {
            "name": "Matumizi ya Lugha (Language Use)",
            "substrands": [
                {
                    "name": "Isimujamii (Sociolinguistics)",
                    "lessons": 10,
                    "slos": [
                        {
                            "name": "Kueleza dhana ya isimujamii",
                            "description": "Explain concept of sociolinguistics and registers in communication",
                            "learning_activities": {
                                "introduction": "Explain concept of sociolinguistics",
                                "development": "Research importance of sociolinguistics. Present findings using digital devices",
                                "conclusion": "Explain rules of language use (topic, age, status). Explain concept of registers",
                                "extended": "Communicate applying appropriate rules of language use in different contexts",
                                "resources": ["Textbooks", "Digital devices", "Internet resources"],
                                "assessment": ["Discussions", "Presentations", "Quizzes"]
                            },
                            "competencies": ["Communication and Collaboration", "Self-Efficacy"],
                            "values": ["Unity", "Respect", "Responsibility"],
                            "pcis": ["Social Awareness", "Appropriate Communication"],
                            "inquiry_questions": ["What is benefit of sociolinguistics in communication?"]
                        }
                    ]
                }
            ]
        }
    ]
}

# ============================================================================
# LITERATURE IN ENGLISH CURRICULUM DATA
# ============================================================================

LITERATURE_ENGLISH_DATA = {
    "name": "Literature in English",
    "strands": [
        {
            "name": "Oral Literature",
            "substrands": [
                {
                    "name": "Introduction to Oral Literature",
                    "lessons": 4,
                    "slos": [
                        {
                            "name": "Identify genres of oral literature",
                            "description": "Identify genres of oral literature and analyse their features and functions",
                            "learning_activities": {
                                "introduction": "Search online or offline for meaning of oral literature",
                                "development": "Listen to recordings on genres of oral literature. Summarise features of oral literature",
                                "conclusion": "Peer review each other's work. Brainstorm on functions of oral literature",
                                "extended": "Present functions through mind map",
                                "resources": ["Online/offline resources", "Audio recordings", "Mind mapping tools"],
                                "assessment": ["Peer review", "Presentations", "Mind maps"]
                            },
                            "competencies": ["Communication and Collaboration", "Learning to Learn"],
                            "values": ["Responsibility", "Unity"],
                            "pcis": ["Social Cohesion"],
                            "inquiry_questions": ["Why is oral literature important in society?"]
                        }
                    ]
                },
                {
                    "name": "Oral Narratives",
                    "lessons": 4,
                    "slos": [
                        {
                            "name": "Identify features of oral narratives",
                            "description": "Identify features of oral narratives and analyse different types for literary analysis",
                            "learning_activities": {
                                "introduction": "Watch narration of oral narrative from video. Discuss meaning and features",
                                "development": "Narrate oral narrative to class for peer review. Identify oral features",
                                "conclusion": "Search online or offline for features. Present findings",
                                "extended": "Collaborate to discuss lessons drawn from narratives",
                                "resources": ["Video resources", "Online/offline sources", "Print/electronic sources"],
                                "assessment": ["Peer review", "Presentations", "Discussions"]
                            },
                            "competencies": ["Communication and Collaboration", "Critical Thinking and Problem Solving"],
                            "values": ["Social Justice", "Peace"],
                            "pcis": ["Learner support programmes"],
                            "inquiry_questions": ["Why is it important to study oral narratives?"]
                        }
                    ]
                },
                {
                    "name": "Songs and Oral Poetry",
                    "lessons": 4,
                    "slos": [
                        {
                            "name": "Identify features of songs",
                            "description": "Identify features of songs for literary analysis and analyse performance of lullabies",
                            "learning_activities": {
                                "introduction": "Listen to oral song from audio or online source",
                                "development": "Discuss features of songs. Search for features from online/offline sources",
                                "conclusion": "Team up to sing common lullabies. Listen to lullaby and discuss characteristics",
                                "extended": "Present responses for peer review. Summarise and display",
                                "resources": ["Audio/online sources", "Charts"],
                                "assessment": ["Chart presentations", "Peer review", "Performances"]
                            },
                            "competencies": ["Digital Literacy", "Learning to Learn"],
                            "values": ["Unity", "Love"],
                            "pcis": ["Citizenship", "Child care and protection"],
                            "inquiry_questions": ["Why do people sing songs?"]
                        }
                    ]
                },
                {
                    "name": "Short Forms of Oral Literature",
                    "lessons": 4,
                    "slos": [
                        {
                            "name": "Identify features of short forms",
                            "description": "Identify features of short forms of oral literature (proverbs, riddles, tongue twisters) and create them",
                            "learning_activities": {
                                "introduction": "Brainstorm on types of short forms of oral literature",
                                "development": "Search for meanings. Read variety of short forms and identify features",
                                "conclusion": "Discuss functions. Collaborate and create short forms",
                                "extended": "Conduct peer review and perform in class. Display in portfolio",
                                "resources": ["Print/non-print sources"],
                                "assessment": ["Presentations", "Performances", "Portfolio"]
                            },
                            "competencies": ["Critical Thinking and Problem Solving", "Citizenship"],
                            "values": ["Social Justice", "Integrity"],
                            "pcis": ["Citizenship", "Cultural preservation"],
                            "inquiry_questions": ["How do short forms enhance creativity and imagination?"]
                        }
                    ]
                }
            ]
        },
        {
            "name": "Poetry",
            "substrands": [
                {
                    "name": "Appreciating Poetry",
                    "lessons": 4,
                    "slos": [
                        {
                            "name": "Identify elements of poetry",
                            "description": "Identify elements of a poem from Kenya and analyse them for comprehension",
                            "learning_activities": {
                                "introduction": "Brainstorm on meaning of poetry and elements of poems from Kenya",
                                "development": "Search for elements from online/offline sources. Peer review findings",
                                "conclusion": "Present findings to class. Collaborate to discuss elements of poems",
                                "extended": "Make notes on elements of poems on environmental conservation",
                                "resources": ["Online/offline sources", "Poems from Kenya"],
                                "assessment": ["Peer review", "Class discussions", "Notes"]
                            },
                            "competencies": ["Communication and Collaboration", "Digital Literacy"],
                            "values": ["Unity", "Respect"],
                            "pcis": ["Environmental conservation", "Social cohesion"],
                            "inquiry_questions": ["Why do we study poetry?"]
                        }
                    ]
                },
                {
                    "name": "Types of Poems",
                    "lessons": 10,
                    "slos": [
                        {
                            "name": "Identify characteristics of poem types",
                            "description": "Identify characteristics of free verse, blank verse, sonnet, and narrative poems",
                            "learning_activities": {
                                "introduction": "Search for meaning of different poem types online/offline",
                                "development": "Share findings. Read and recite different types of poems",
                                "conclusion": "Discuss characteristics and subject matter. Summarise in charts",
                                "extended": "Collaborate to perform different types of poems in class and forums",
                                "resources": ["Online/offline resources", "Poetry collections"],
                                "assessment": ["Charts", "Performances", "Class presentations"]
                            },
                            "competencies": ["Critical Thinking and Problem Solving", "Learning to Learn"],
                            "values": ["Unity"],
                            "pcis": ["Citizenship Education", "Social cohesion"],
                            "inquiry_questions": ["How are poems classified?", "How can we make performance of poems enjoyable?"]
                        }
                    ]
                },
                {
                    "name": "Creating Poetry",
                    "lessons": 4,
                    "slos": [
                        {
                            "name": "Explain process of writing a poem",
                            "description": "Explain process involved in writing a poem and create poems on given topics",
                            "learning_activities": {
                                "introduction": "Search for steps involved in writing a poem",
                                "development": "Identify topic. Brainstorm for ideas, images, and phrases. Create structure and determine style",
                                "conclusion": "Draft poem on environmental education. Revise and edit for coherence",
                                "extended": "Share poem for feedback. Display on noticeboard or e-portfolio",
                                "resources": ["Online/offline resources", "Writing guides"],
                                "assessment": ["Poem drafting", "Peer feedback", "Portfolio display"]
                            },
                            "competencies": ["Communication and Collaboration", "Self-Efficacy"],
                            "values": ["Respect", "Integrity"],
                            "pcis": ["Environmental Education", "Climate change"],
                            "inquiry_questions": ["How can one become a good poet?", "How can you tell whether a poem is well written?"]
                        }
                    ]
                },
                {
                    "name": "Language and Style in Poetry",
                    "lessons": 2,
                    "slos": [
                        {
                            "name": "Examine imagery in poems",
                            "description": "Examine imagery (simile, metaphor) in poems for literary analysis",
                            "learning_activities": {
                                "introduction": "Brainstorm on imagery in poetry and share with peers",
                                "development": "Search meaning of imagery from print/non-print sources. Read poems and identify similes and metaphors",
                                "conclusion": "Share findings with peers. Collaborate to use imagery to write poems",
                                "extended": "Discuss significance of imagery in poems for literary appreciation",
                                "resources": ["Poems", "Print/non-print sources"],
                                "assessment": ["Poem writing", "Discussions"]
                            },
                            "competencies": ["Critical Thinking and Problem Solving", "Learning to Learn"],
                            "values": ["Peace", "Integrity"],
                            "pcis": ["Social Cohesion"],
                            "inquiry_questions": ["How does use of imagery promote imagination and creativity?"]
                        }
                    ]
                }
            ]
        },
        {
            "name": "Fiction and Non-Fiction",
            "substrands": [
                {
                    "name": "Fiction - Novel from Kenya",
                    "lessons": 12,
                    "slos": [
                        {
                            "name": "Explain features of prose fiction",
                            "description": "Explain features of prose fiction and examine elements of history in Kenyan novels",
                            "learning_activities": {
                                "introduction": "Team up to search for features of prose fiction from Kenya",
                                "development": "Make presentation on features for peer review. Discuss elements of history",
                                "conclusion": "Collaborate to write synopsis of novel. Arrange events chronologically in flow chart",
                                "extended": "Share work with peers for feedback",
                                "resources": ["Online/offline sources", "Set novel from Kenya"],
                                "assessment": ["Presentations", "Peer review", "Flow charts", "Synopsis"]
                            },
                            "competencies": ["Creativity and Imagination", "Self-Efficacy"],
                            "values": ["Respect", "Unity"],
                            "pcis": ["Patriotism", "Cultural identity"],
                            "inquiry_questions": ["How has history influenced prose fiction in Kenya?"]
                        }
                    ]
                },
                {
                    "name": "Fiction - Character and Theme Analysis",
                    "lessons": 12,
                    "slos": [
                        {
                            "name": "Identify characters and themes",
                            "description": "Identify characters and their traits from set novel and analyse themes",
                            "learning_activities": {
                                "introduction": "Read set novel and collaborate to write sequence of events",
                                "development": "Identify characters and discuss their traits. Relate cultural elements to Kenya",
                                "conclusion": "Discuss themes. Link characters to real life and draw lessons",
                                "extended": "Summarise characters and themes in graphic organiser for noticeboard",
                                "resources": ["Set novel"],
                                "assessment": ["Graphic organizers", "Presentations"]
                            },
                            "competencies": ["Critical Thinking and Problem Solving", "Citizenship"],
                            "values": ["Social Justice", "Respect"],
                            "pcis": ["Social awareness skills"],
                            "inquiry_questions": ["Why should one read a novel?"]
                        }
                    ]
                },
                {
                    "name": "Fiction - Language and Style",
                    "lessons": 8,
                    "slos": [
                        {
                            "name": "Identify language and style in novel",
                            "description": "Identify language and style in novel and relate language use to values",
                            "learning_activities": {
                                "introduction": "Read novel and discuss language and style for peer review",
                                "development": "Search for stylistic devices and language use online/offline. Discuss and present findings",
                                "conclusion": "Link language use to real life concerns and draw moral lessons",
                                "extended": "Summarise language use and stylistic devices in graphic organiser",
                                "resources": ["Novel", "Online/offline resources"],
                                "assessment": ["Peer review", "Graphic organizers"]
                            },
                            "competencies": ["Critical Thinking and Problem Solving", "Citizenship"],
                            "values": ["Social Justice", "Integrity"],
                            "pcis": ["Citizenship skills", "Social cohesion"],
                            "inquiry_questions": ["Why is style important in reading a novel?"]
                        }
                    ]
                },
                {
                    "name": "Non-Fiction - Personal Journal",
                    "lessons": 8,
                    "slos": [
                        {
                            "name": "Identify structure of personal journal",
                            "description": "Identify structure of personal journal and analyse content and style",
                            "learning_activities": {
                                "introduction": "Brainstorm on meaning of life-writing and present findings",
                                "development": "Conduct online search on characteristics of personal journals. Discuss structure on mind map",
                                "conclusion": "Read sample personal journal. Discuss content, language and style",
                                "extended": "Make entry of personal journal from personal experiences. Peer review and organise in portfolio",
                                "resources": ["Online search facilities", "Sample personal journals"],
                                "assessment": ["Mind maps", "Journal entries", "Portfolio"]
                            },
                            "competencies": ["Digital Literacy", "Critical Thinking and Problem Solving"],
                            "values": ["Unity", "Responsibility"],
                            "pcis": ["Self-awareness"],
                            "inquiry_questions": ["Why is it important to keep journals?"]
                        }
                    ]
                },
                {
                    "name": "Non-Fiction - Autobiography",
                    "lessons": 4,
                    "slos": [
                        {
                            "name": "Explain structure of autobiography",
                            "description": "Explain structure of autobiography and analyse main ideas addressed",
                            "learning_activities": {
                                "introduction": "Conduct reading session to read autobiography from Kenya",
                                "development": "Summarise structure on graphic organiser. Brainstorm main ideas and PCIs",
                                "conclusion": "Search for information on process of writing autobiography",
                                "extended": "Write section of own life story following outlined process. Share drafts for peer review",
                                "resources": ["Autobiography from Kenya", "Online/offline sources"],
                                "assessment": ["Graphic organizers", "Portfolio"]
                            },
                            "competencies": ["Creativity and Imagination", "Citizenship"],
                            "values": ["Peace", "Respect"],
                            "pcis": ["Nationalism", "Self-reflection"],
                            "inquiry_questions": ["Why do people write their own life stories?"]
                        }
                    ]
                },
                {
                    "name": "Non-Fiction - Memoir",
                    "lessons": 4,
                    "slos": [
                        {
                            "name": "Explain features of memoir",
                            "description": "Explain features of memoir and study structure, content and values",
                            "learning_activities": {
                                "introduction": "Read memoir from given text",
                                "development": "Collaborate and brainstorm on features of memoir. Search online/offline for structure and content",
                                "conclusion": "Summarise information in graphic organiser. Display for peer review",
                                "extended": "Discuss values in memoirs and emulate them",
                                "resources": ["Memoir", "Online/offline resources"],
                                "assessment": ["Graphic organizers", "Peer review", "Discussion"]
                            },
                            "competencies": ["Creativity and Imagination", "Self-Efficacy"],
                            "values": ["Unity", "Respect"],
                            "pcis": ["Citizenship", "Values education"],
                            "inquiry_questions": ["How do memoirs influence development of values in society?"]
                        }
                    ]
                },
                {
                    "name": "Fiction - Short Stories from Kenya",
                    "lessons": 5,
                    "slos": [
                        {
                            "name": "Examine features of short stories",
                            "description": "Examine features of short stories from Kenya and identify elements of history",
                            "learning_activities": {
                                "introduction": "Search for features of short stories from online/offline sources",
                                "development": "Discuss features of short stories from Kenya. Peer review",
                                "conclusion": "Identify elements of history from short stories in Kenya",
                                "extended": "Summarise findings using graphic organisers",
                                "resources": ["Anthology of short stories from Kenya", "Online/offline sources"],
                                "assessment": ["Presentations", "Peer review", "Graphic organizers"]
                            },
                            "competencies": ["Creativity and Imagination", "Digital Literacy"],
                            "values": ["Social Justice", "Unity"],
                            "pcis": ["Citizenship", "Equity and non-discrimination"],
                            "inquiry_questions": ["How has history and culture influenced the short story in Kenya?"]
                        }
                    ]
                },
                {
                    "name": "Fiction - Drama and Play Performance",
                    "lessons": 8,
                    "slos": [
                        {
                            "name": "Identify performance techniques",
                            "description": "Identify techniques in play for performance and act a scene employing performance techniques",
                            "learning_activities": {
                                "introduction": "Search for performance techniques online/offline. Present findings for peer review",
                                "development": "Watch live or video performance of play. Discuss performance techniques",
                                "conclusion": "Perform an act or scene of play. Critique performance techniques",
                                "extended": "Summarise performance techniques",
                                "resources": ["Live/video performances of plays"],
                                "assessment": ["Peer review", "Critiques", "Performances"]
                            },
                            "competencies": ["Learning to Learn", "Creativity and Imagination"],
                            "values": ["Respect", "Peace"],
                            "pcis": ["Social Cohesion"],
                            "inquiry_questions": ["Why are performance techniques important in a play?"]
                        }
                    ]
                }
            ]
        },
        {
            "name": "Oral Literature Fieldwork",
            "substrands": [
                {
                    "name": "Oral Literature Fieldwork Project",
                    "lessons": 4,
                    "slos": [
                        {
                            "name": "Explain preparation process for fieldwork",
                            "description": "Explain preparation process for fieldwork, objectives, methods of data collection and ethical considerations",
                            "learning_activities": {
                                "introduction": "Brainstorm on preparation process for fieldwork and present findings",
                                "development": "Explore methods, objectives, and ethical considerations in fieldwork",
                                "conclusion": "Summarise information in graphic organiser. Discuss value of fieldwork",
                                "extended": "Conduct field work research on short forms. Share findings with peers",
                                "resources": ["Fieldwork resources", "Graphic organizers"],
                                "assessment": ["Presentations", "Fieldwork research", "Sharing findings"]
                            },
                            "competencies": ["Communication and Collaboration", "Self-Efficacy"],
                            "values": ["Unity", "Respect"],
                            "pcis": ["Citizenship", "Research ethics"],
                            "inquiry_questions": ["Why is fieldwork important in oral literature?"]
                        }
                    ]
                }
            ]
        }
    ]
}

# ============================================================================
# PHYSICS CURRICULUM DATA
# ============================================================================

PHYSICS_DATA = {
    "name": "Physics",
    "strands": [
        {
            "name": "Mechanics and Thermal Physics",
            "substrands": [
                {
                    "name": "Introduction to Physics",
                    "lessons": 6,
                    "slos": [
                        {
                            "name": "Explain Physics as a body of knowledge",
                            "description": "Explain Physics as a body of knowledge in science and describe branches of Physics",
                            "learning_activities": {
                                "introduction": "Work with others to search for meaning of Physics as branch of science",
                                "development": "Discuss with peers main branches of Physics. Discuss importance of Physics in day-to-day life",
                                "conclusion": "Discuss relationship of Physics with other fields of study",
                                "extended": "Engage resource persons or use print/non-print media for career opportunities. Design and present career charts",
                                "resources": ["Print or non-print media"],
                                "assessment": ["Explaining importance of Physics", "Career opportunities presentation"]
                            },
                            "competencies": ["Communication and Collaboration", "Learning to Learn", "Digital Literacy"],
                            "values": ["Responsibility", "Respect"],
                            "pcis": ["Gender Disparity", "Myths and misconceptions"],
                            "inquiry_questions": ["How is Physics relevant in day to day life?"]
                        }
                    ]
                },
                {
                    "name": "Pressure",
                    "lessons": 25,
                    "slos": [
                        {
                            "name": "Describe atmospheric pressure",
                            "description": "Describe atmospheric pressure and demonstrate its existence and factors affecting pressure in fluids",
                            "learning_activities": {
                                "introduction": "Discuss with peers meaning of atmospheric pressure",
                                "development": "Carry out activities to demonstrate existence of atmospheric pressure. Investigate factors affecting pressure",
                                "conclusion": "Derive and use equation P = ρgh. Demonstrate principle of transmission of pressure",
                                "extended": "Use print/non-print media to search for applications of pressure",
                                "resources": ["Print or non-print media", "Laboratory equipment"],
                                "assessment": ["Explaining applications", "Determining pressure in fluids"]
                            },
                            "competencies": ["Communication and Collaboration", "Digital Literacy"],
                            "values": ["Love", "Respect"],
                            "pcis": ["Environmental Issues", "Climate change"],
                            "inquiry_questions": ["How does density, acceleration due to gravity and depth affect pressure in fluid?"]
                        }
                    ]
                },
                {
                    "name": "Mechanical Properties of Materials",
                    "lessons": 10,
                    "slos": [
                        {
                            "name": "Explain mechanical properties of materials",
                            "description": "Explain mechanical properties of materials (ductility, malleability, elasticity, brittleness, strength, hardness, stiffness)",
                            "learning_activities": {
                                "introduction": "Discuss with peers mechanical properties of locally available materials",
                                "development": "Carry out activities to demonstrate mechanical properties. Determine relationship between tensile force and extension",
                                "conclusion": "Use digital devices to search for industrial applications. Use mathematical relationships for tensile stress, strain, modulus",
                                "extended": "Research applications of mechanical properties in engineering",
                                "resources": ["Digital devices", "Laboratory equipment"],
                                "assessment": ["Explaining applications", "Determining tensile stress and strain"]
                            },
                            "competencies": ["Communication and Collaboration", "Critical Thinking and Problem Solving"],
                            "values": ["Responsibility", "Respect", "Integrity"],
                            "pcis": ["Safety and Security", "Material choices"],
                            "inquiry_questions": ["Why does a string snap easily compared to a spring?", "Why is it important to study mechanical properties?"]
                        }
                    ]
                },
                {
                    "name": "Temperature and Thermal Expansion",
                    "lessons": 10,
                    "slos": [
                        {
                            "name": "Explain meaning of temperature",
                            "description": "Explain meaning of temperature and measure temperature using different technologies",
                            "learning_activities": {
                                "introduction": "Discuss meaning of temperature",
                                "development": "Measure temperature using various technologies (liquid expansion, bimetallic, thermocouples). Search digital media for more information",
                                "conclusion": "Demonstrate thermal expansion and contraction in solids and fluids. Determine linear expansivity",
                                "extended": "Discuss applications of thermal expansion in day-to-day life",
                                "resources": ["Digital media", "Print/non-print media", "Laboratory equipment"],
                                "assessment": ["Describing applications", "Investigating thermal expansion"]
                            },
                            "competencies": ["Citizenship", "Digital Literacy"],
                            "values": ["Peace", "Patriotism"],
                            "pcis": ["Fire safety"],
                            "inquiry_questions": ["Why is lid of a sufuria made wider?", "Why does glass bottle break when water in it freezes?"]
                        }
                    ]
                },
                {
                    "name": "Moments and Equilibrium",
                    "lessons": 15,
                    "slos": [
                        {
                            "name": "Determine center of gravity",
                            "description": "Determine center of gravity of regular and irregular objects and identify states of equilibrium",
                            "learning_activities": {
                                "introduction": "Design and carry out activities to determine center of gravity",
                                "development": "Demonstrate stability, instability, and neutral equilibrium. Discuss meaning of moments of force",
                                "conclusion": "Demonstrate turning effect of forces, torque and couple. Investigate factors affecting stability",
                                "extended": "Use print/non-print media to search for applications of torque, couples, and stability",
                                "resources": ["Print/non-print media", "Laboratory equipment"],
                                "assessment": ["Verifying principle of moments", "Describing applications"]
                            },
                            "competencies": ["Creativity and Imagination", "Citizenship"],
                            "values": ["Unity", "Integrity"],
                            "pcis": ["Road safety"],
                            "inquiry_questions": ["How does stability of bodies affect design of their structures?"]
                        }
                    ]
                },
                {
                    "name": "Energy, Work, Power and Machines",
                    "lessons": 18,
                    "slos": [
                        {
                            "name": "Explain energy, work and power",
                            "description": "Explain meaning of energy, work and power in relation to machines and demonstrate energy transformation",
                            "learning_activities": {
                                "introduction": "Discuss with peers meaning of energy, work, and power",
                                "development": "Demonstrate concepts of energy, work, power, and machines. Perform experiments on mechanical energy transformations",
                                "conclusion": "Apply mathematical relationships. Demonstrate law of conservation of mechanical energy",
                                "extended": "Use locally available materials to construct simple machines",
                                "resources": ["Simple apparatus", "Print/non-print media", "Locally available materials"],
                                "assessment": ["Demonstrating energy transformation", "Describing applications of machines"]
                            },
                            "competencies": ["Communication and Collaboration", "Critical Thinking and Problem Solving"],
                            "values": ["Love", "Responsibility"],
                            "pcis": ["Life skills", "Environmental education"],
                            "inquiry_questions": ["How do machines make work easier?"]
                        }
                    ]
                }
            ]
        },
        {
            "name": "Waves and Optics",
            "substrands": [
                {
                    "name": "Properties of Waves",
                    "lessons": 24,
                    "slos": [
                        {
                            "name": "Explain wave properties",
                            "description": "Explain wave properties in real-life situations and demonstrate formation of stationary waves",
                            "learning_activities": {
                                "introduction": "Discuss meaning of wave properties and their applications",
                                "development": "Perform experiments to demonstrate wave properties. Sketch wave patterns and present",
                                "conclusion": "Demonstrate formation and properties of stationary waves",
                                "extended": "Use print/non-print media to search for information on sound waves and Doppler's effect",
                                "resources": ["Print/non-print media", "Laboratory equipment"],
                                "assessment": ["Describing formation and properties of waves"]
                            },
                            "competencies": ["Learning to Learn", "Self-Efficacy"],
                            "values": ["Social Justice", "Patriotism"],
                            "pcis": ["Noise pollution"],
                            "inquiry_questions": ["How do you relate waves to basic properties of light?", "Where is Doppler's effect applied?"]
                        }
                    ]
                },
                {
                    "name": "Radioactivity and Stability of Isotopes",
                    "lessons": 24,
                    "slos": [
                        {
                            "name": "Explain terminologies in radioactivity",
                            "description": "Explain terminologies used in radioactivity and identify types and properties of radioactive emissions",
                            "learning_activities": {
                                "introduction": "Search and discuss terms used in radioactivity",
                                "development": "Discuss types and properties of radiations. Make charts illustrating properties. Write nuclear equations",
                                "conclusion": "Demonstrate detection of radioactive emissions. Determine half-life using formula and graphical methods",
                                "extended": "Search for applications and dangers of radioactivity",
                                "resources": ["Print/non-print media", "Charts", "Cloud chamber", "Geiger muller"],
                                "assessment": ["Illustrating radionuclide stability", "Describing applications and safety precautions"]
                            },
                            "competencies": ["Imagination and Creativity", "Self-Efficacy"],
                            "values": ["Respect", "Peace"],
                            "pcis": ["Peace education", "Environmental conservation"],
                            "inquiry_questions": ["How is radioactivity important in day-to-day life?", "What are risks of exposure to radiation?"]
                        }
                    ]
                }
            ]
        },
        {
            "name": "Electricity and Magnetism",
            "substrands": [
                {
                    "name": "Electrostatics",
                    "lessons": 10,
                    "slos": [
                        {
                            "name": "Explain origin of charges",
                            "description": "Explain origin of charges and describe methods of charging a conductor",
                            "learning_activities": {
                                "introduction": "Discuss origin of charges and law of electrostatics",
                                "development": "Perform experiments to demonstrate generation of static charges. Discuss ways of charging conductors",
                                "conclusion": "Describe features and functions of electroscope. Construct simple leaf electroscope",
                                "extended": "Use print/non-print media to investigate charge distribution and applications of electrostatics",
                                "resources": ["Print/non-print media", "Resource persons", "Laboratory equipment"],
                                "assessment": ["Explaining charging and uses of electroscope", "Describing applications"]
                            },
                            "competencies": ["Learning to Learn", "Self-Efficacy"],
                            "values": ["Responsibility", "Love"],
                            "pcis": ["Safety and Security"],
                            "inquiry_questions": ["How do lightning arrestors work?", "How do materials get charged?"]
                        }
                    ]
                },
                {
                    "name": "Current Electricity",
                    "lessons": 18,
                    "slos": [
                        {
                            "name": "Explain terminologies in current electricity",
                            "description": "Explain terminologies used in current electricity and verify relationships (V=IR, E=I(R+r))",
                            "learning_activities": {
                                "introduction": "Discuss meaning of current, potential difference, electromotive force, and internal resistance",
                                "development": "Perform experiments to investigate relationships. Classify types of resistors. Investigate factors affecting resistance",
                                "conclusion": "Determine resistance using various methods. Carry out experiments on power relationships",
                                "extended": "Discuss applications of heating effect of electric current",
                                "resources": ["Laboratory equipment (ammeter, voltmeter, resistors, power supply)"],
                                "assessment": ["Describing applications", "Determining resistance"]
                            },
                            "competencies": ["Critical Thinking and Problem Solving", "Learning to Learn"],
                            "values": ["Responsibility", "Respect"],
                            "pcis": ["Safety"],
                            "inquiry_questions": ["How is current electricity applicable in day-to-day life?", "Why are resistors used in electrical circuits?"]
                        }
                    ]
                },
                {
                    "name": "Introduction to Electronics",
                    "lessons": 6,
                    "slos": [
                        {
                            "name": "Explain insulators, conductors, semiconductors",
                            "description": "Explain meaning of insulator, conductor, semiconductor, and superconductor and distinguish between them",
                            "learning_activities": {
                                "introduction": "Discuss meaning of insulator, conductor, semiconductor, and superconductor",
                                "development": "Perform experiments to investigate electrical behavior with varying temperatures. Use diagrams to distinguish using energy band theory",
                                "conclusion": "Discuss intrinsic and extrinsic semiconductors. Research formation of p-type and n-type semiconductors",
                                "extended": "Discuss applications of these materials. Search for more information from relevant sources",
                                "resources": ["Digital devices", "Print/non-print media"],
                                "assessment": ["Describing applications of conductors, semiconductors, insulators, superconductors"]
                            },
                            "competencies": ["Critical Thinking and Problem Solving", "Digital Literacy"],
                            "values": ["Social Justice", "Unity"],
                            "pcis": ["Citizenship education"],
                            "inquiry_questions": ["How does temperature affect resistance of conductors and semiconductors?", "What is significance of semiconductors?"]
                        }
                    ]
                }
            ]
        },
        {
            "name": "Environmental and Space Physics",
            "substrands": [
                {
                    "name": "Greenhouse Effect and Climate Change",
                    "lessons": 5,
                    "slos": [
                        {
                            "name": "Explain greenhouse effect and climate change",
                            "description": "Explain greenhouse effect and climate change, outline contributing factors and describe mitigating factors",
                            "learning_activities": {
                                "introduction": "Discuss meaning of greenhouse effect and climate change",
                                "development": "Discuss factors leading to greenhouse effect. Demonstrate effects of climate change with peers",
                                "conclusion": "Discuss role of human activities. Outline mitigating factors",
                                "extended": "Use print/non-print media to search for more information",
                                "resources": ["Reference materials", "Resource persons", "Digital materials", "Print/non-print media"],
                                "assessment": ["Describing impact of climate change"]
                            },
                            "competencies": ["Communication and Collaboration", "Critical Thinking and Problem Solving", "Digital Literacy"],
                            "values": ["Peace", "Unity"],
                            "pcis": ["Global warming"],
                            "inquiry_questions": ["How do human actions impact climate change?", "How does ozone layer depletion threaten our environment?"]
                        }
                    ]
                },
                {
                    "name": "Introduction to Space Physics",
                    "lessons": 6,
                    "slos": [
                        {
                            "name": "Describe big bang theory",
                            "description": "Describe big bang theory of origin of universe and classify celestial bodies",
                            "learning_activities": {
                                "introduction": "Discuss big bang theory",
                                "development": "Use digital media to observe celestial bodies and planetary motion. Model planetary motion",
                                "conclusion": "Discuss methods of exploring the universe",
                                "extended": "Discuss careers available in Astrophysics and space exploration",
                                "resources": ["Digital media"],
                                "assessment": ["Explaining evolution of astrophysics and space exploration"]
                            },
                            "competencies": ["Creativity and Imagination", "Digital Literacy"],
                            "values": ["Integrity", "Love"],
                            "pcis": ["Life skills", "Self-management skills"],
                            "inquiry_questions": ["How was the universe/earth formed?", "How do we benefit from Astrophysics?"]
                        }
                    ]
                }
            ]
        }
    ]
}

# ============================================================================
# DATABASE OPERATIONS
# ============================================================================

async def get_or_create_id(collection_name, query, new_doc=None):
    """Get existing document ID or create new one"""
    doc = await db[collection_name].find_one(query)
    if doc:
        return str(doc["_id"])
    if new_doc:
        result = await db[collection_name].insert_one(new_doc)
        return str(result.inserted_id)
    return None

async def get_grade_10_id():
    """Get Grade 10 ID from database"""
    grade = await db.grades.find_one({"name": "Grade 10"})
    if grade:
        return str(grade["_id"])
    # Create Grade 10 if it doesn't exist
    result = await db.grades.insert_one({"name": "Grade 10", "order": 10})
    return str(result.inserted_id)

async def get_competency_ids(competency_names):
    """Get competency IDs from database"""
    ids = []
    for name in competency_names:
        comp = await db.competencies.find_one({"name": {"$regex": name, "$options": "i"}})
        if comp:
            ids.append(str(comp["_id"]))
    return ids

async def get_value_ids(value_names):
    """Get value IDs from database"""
    ids = []
    for name in value_names:
        val = await db.values.find_one({"name": {"$regex": name, "$options": "i"}})
        if val:
            ids.append(str(val["_id"]))
    return ids

async def get_pci_ids(pci_names):
    """Get PCI IDs from database"""
    ids = []
    for name in pci_names:
        pci = await db.pcis.find_one({"name": {"$regex": name, "$options": "i"}})
        if pci:
            ids.append(str(pci["_id"]))
    return ids

async def delete_existing_subject_data(subject_name, grade_id):
    """Delete existing data for a subject before re-seeding"""
    print(f"  Deleting existing data for {subject_name}...")
    
    # Find the subject
    subject = await db.subjects.find_one({"name": subject_name, "gradeIds": grade_id})
    if not subject:
        print(f"    No existing subject found for {subject_name}")
        return
    
    subject_id = str(subject["_id"])
    
    # Find all strands for this subject
    strands = await db.strands.find({"subjectId": subject_id}).to_list(1000)
    strand_ids = [str(s["_id"]) for s in strands]
    
    # Find all substrands for these strands
    substrands = await db.substrands.find({"strandId": {"$in": strand_ids}}).to_list(10000)
    substrand_ids = [str(s["_id"]) for s in substrands]
    
    # Find all SLOs for these substrands
    slos = await db.slos.find({"substrandId": {"$in": substrand_ids}}).to_list(10000)
    slo_ids = [str(s["_id"]) for s in slos]
    
    # Delete in reverse order
    if slo_ids:
        await db.slo_mappings.delete_many({"sloId": {"$in": slo_ids}})
        await db.learning_activities.delete_many({"sloId": {"$in": slo_ids}})
        await db.learning_activities.delete_many({"substrandId": {"$in": substrand_ids}})
        await db.slos.delete_many({"substrandId": {"$in": substrand_ids}})
        print(f"    Deleted {len(slo_ids)} SLOs and related data")
    
    if substrand_ids:
        await db.substrands.delete_many({"strandId": {"$in": strand_ids}})
        print(f"    Deleted {len(substrand_ids)} substrands")
    
    if strand_ids:
        await db.strands.delete_many({"subjectId": subject_id})
        print(f"    Deleted {len(strand_ids)} strands")
    
    # Delete the subject entry for this grade only (might have other grades)
    if len(subject.get("gradeIds", [])) == 1:
        await db.subjects.delete_one({"_id": subject["_id"]})
        print(f"    Deleted subject {subject_name}")
    else:
        # Remove this grade from the subject's gradeIds
        await db.subjects.update_one(
            {"_id": subject["_id"]},
            {"$pull": {"gradeIds": grade_id}}
        )
        print(f"    Removed Grade 10 from subject {subject_name}")

async def seed_subject_data(subject_data, grade_id):
    """Seed data for a single subject"""
    subject_name = subject_data["name"]
    print(f"\n{'='*60}")
    print(f"Seeding {subject_name}...")
    print(f"{'='*60}")
    
    # Delete existing data first
    await delete_existing_subject_data(subject_name, grade_id)
    
    # Create or update subject
    existing_subject = await db.subjects.find_one({"name": subject_name})
    if existing_subject:
        # Add grade_id if not already present
        if grade_id not in existing_subject.get("gradeIds", []):
            await db.subjects.update_one(
                {"_id": existing_subject["_id"]},
                {"$addToSet": {"gradeIds": grade_id}}
            )
        subject_id = str(existing_subject["_id"])
    else:
        result = await db.subjects.insert_one({
            "name": subject_name,
            "gradeIds": [grade_id]
        })
        subject_id = str(result.inserted_id)
    
    print(f"  Subject ID: {subject_id}")
    
    # Counters
    strand_count = 0
    substrand_count = 0
    slo_count = 0
    learning_activity_count = 0
    slo_mapping_count = 0
    
    # Seed strands
    for strand_data in subject_data["strands"]:
        strand_result = await db.strands.insert_one({
            "name": strand_data["name"],
            "subjectId": subject_id
        })
        strand_id = str(strand_result.inserted_id)
        strand_count += 1
        print(f"    Strand: {strand_data['name']}")
        
        # Seed substrands
        for substrand_data in strand_data["substrands"]:
            substrand_result = await db.substrands.insert_one({
                "name": substrand_data["name"],
                "strandId": strand_id
            })
            substrand_id = str(substrand_result.inserted_id)
            substrand_count += 1
            print(f"      Substrand: {substrand_data['name']} ({substrand_data['lessons']} lessons)")
            
            # Seed SLOs
            for slo_data in substrand_data["slos"]:
                slo_result = await db.slos.insert_one({
                    "name": slo_data["name"],
                    "description": slo_data["description"],
                    "substrandId": substrand_id
                })
                slo_id = str(slo_result.inserted_id)
                slo_count += 1
                
                # Get competency, value, and PCI IDs
                competency_ids = await get_competency_ids(slo_data.get("competencies", []))
                value_ids = await get_value_ids(slo_data.get("values", []))
                pci_ids = await get_pci_ids(slo_data.get("pcis", []))
                
                # Create SLO mapping
                await db.slo_mappings.insert_one({
                    "sloId": slo_id,
                    "competencyIds": competency_ids,
                    "valueIds": value_ids,
                    "pciIds": pci_ids,
                    "assessmentIds": []
                })
                slo_mapping_count += 1
                
                # Create learning activities
                activities = slo_data.get("learning_activities", {})
                if activities:
                    await db.learning_activities.insert_one({
                        "substrandId": substrand_id,
                        "sloId": slo_id,
                        "introduction": activities.get("introduction", ""),
                        "development": activities.get("development", ""),
                        "conclusion": activities.get("conclusion", ""),
                        "extended_activities": [activities.get("extended", "")] if activities.get("extended") else [],
                        "learning_resources": activities.get("resources", []),
                        "assessment_methods": activities.get("assessment", []),
                        "inquiry_questions": slo_data.get("inquiry_questions", []),
                        "core_competencies": slo_data.get("competencies", []),
                        "values": slo_data.get("values", []),
                        "pci": slo_data.get("pcis", [])
                    })
                    learning_activity_count += 1
    
    print(f"\n  Summary for {subject_name}:")
    print(f"    Strands: {strand_count}")
    print(f"    Substrands: {substrand_count}")
    print(f"    SLOs: {slo_count}")
    print(f"    Learning Activities: {learning_activity_count}")
    print(f"    SLO Mappings: {slo_mapping_count}")
    
    return {
        "subject": subject_name,
        "strands": strand_count,
        "substrands": substrand_count,
        "slos": slo_count,
        "learning_activities": learning_activity_count,
        "slo_mappings": slo_mapping_count
    }

async def main():
    """Main function to seed all subject data"""
    print("="*60)
    print("Grade 10 Curriculum Data Seeding")
    print("Subjects: Geography, History and Citizenship, Kiswahili Lugha,")
    print("          Literature in English, Physics")
    print("="*60)
    
    # Get Grade 10 ID
    grade_id = await get_grade_10_id()
    print(f"\nGrade 10 ID: {grade_id}")
    
    # All subjects to seed
    subjects = [
        GEOGRAPHY_DATA,
        HISTORY_CITIZENSHIP_DATA,
        KISWAHILI_LUGHA_DATA,
        LITERATURE_ENGLISH_DATA,
        PHYSICS_DATA
    ]
    
    # Seed each subject
    results = []
    for subject_data in subjects:
        result = await seed_subject_data(subject_data, grade_id)
        results.append(result)
    
    # Print final summary
    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)
    
    total_strands = 0
    total_substrands = 0
    total_slos = 0
    total_learning_activities = 0
    total_slo_mappings = 0
    
    for result in results:
        print(f"\n{result['subject']}:")
        print(f"  Strands: {result['strands']}")
        print(f"  Substrands: {result['substrands']}")
        print(f"  SLOs: {result['slos']}")
        print(f"  Learning Activities: {result['learning_activities']}")
        print(f"  SLO Mappings: {result['slo_mappings']}")
        
        total_strands += result['strands']
        total_substrands += result['substrands']
        total_slos += result['slos']
        total_learning_activities += result['learning_activities']
        total_slo_mappings += result['slo_mappings']
    
    print(f"\n{'='*60}")
    print(f"TOTALS:")
    print(f"  Total Strands: {total_strands}")
    print(f"  Total Substrands: {total_substrands}")
    print(f"  Total SLOs: {total_slos}")
    print(f"  Total Learning Activities: {total_learning_activities}")
    print(f"  Total SLO Mappings: {total_slo_mappings}")
    print(f"{'='*60}")
    print("\nSeeding completed successfully!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
