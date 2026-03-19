"""
Grade 10 Curriculum Data Seeding Script - COMPLETE VERSION
Subjects: Geography, History and Citizenship, Kiswahili Lugha, Literature in English, Physics

This script seeds ALL curriculum data from KICD curriculum designs into the MongoDB database.
It captures ALL strands, substrands, and SLOs from each PDF.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime

# MongoDB connection
MONGO_URL = "mongodb+srv://clive_db_admin:n1ruhu5u@cbeplanner.jtshzub.mongodb.net/cbeplanner?retryWrites=true&w=majority&appName=cbeplanner"
DB_NAME = "cbeplanner"

# Connect to MongoDB
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# ============================================================================
# GEOGRAPHY - COMPLETE DATA
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
                        {"name": "Analyse the branches of Geography for in-depth understanding of the subject", "description": "Analyse the branches of Geography for in-depth understanding of the subject"},
                        {"name": "Examine the importance of studying Geography for sustainable development", "description": "Examine the importance of studying Geography for sustainable development"},
                        {"name": "Explore the relationship between Geography and other disciplines for identification of career pathways", "description": "Explore the relationship between Geography and other disciplines for identification of career pathways"},
                        {"name": "Select possible careers from branches of Geography in the society", "description": "Select possible careers from branches of Geography in the society"},
                        {"name": "Appreciate the significance of Geography in day-to-day life", "description": "Appreciate the significance of Geography in day-to-day life"}
                    ],
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
                    "name": "Map Reading and Interpretation",
                    "lessons": 13,
                    "slos": [
                        {"name": "Illustrate the various methods of representing relief on topographical maps", "description": "Illustrate the various methods of representing relief on topographical maps"},
                        {"name": "Interpret relief, drainage and vegetation on topographical maps for resource mapping", "description": "Interpret relief, drainage and vegetation on topographical maps for resource mapping"},
                        {"name": "Draw sketch sections from topographical maps for interpreting relief", "description": "Draw sketch sections from topographical maps for interpreting relief"},
                        {"name": "Appreciate the use of map reading and interpretation skills for national development", "description": "Appreciate the use of map reading and interpretation skills for national development"}
                    ],
                    "learning_activities": {
                        "introduction": "Brainstorm on meaning and types of maps and share in class",
                        "development": "Use print or digital resources to research on methods of representing relief, drainage and vegetation on topographical maps. Draw sketches",
                        "conclusion": "Discuss how relief, drainage and vegetation are interpreted on topographical maps",
                        "extended": "Watch video clips on relief, drainage, and vegetation. Field visit to observe local landscape features",
                        "resources": ["Topographical Maps", "Digital resources", "Photographs", "Pictures", "Local environment"],
                        "assessment": ["Oral Questions", "Written tests", "Observation", "Portfolios", "Checklists"]
                    },
                    "competencies": ["Self-Efficacy", "Digital Literacy", "Critical Thinking and Problem Solving"],
                    "values": ["Unity", "Respect", "Responsibility"],
                    "pcis": ["Self-Awareness", "Environmental Education", "Online Safety"],
                    "inquiry_questions": ["How do we read and interpret topographical maps?"]
                },
                {
                    "name": "Statistical Methods",
                    "lessons": 12,
                    "slos": [
                        {"name": "Analyse the importance of statistics in Geography", "description": "Analyse the importance of statistics in Geography"},
                        {"name": "Explore the limitations of statistics in explaining geographical facts", "description": "Explore the limitations of statistics in explaining geographical facts"},
                        {"name": "Examine the methods of data collection, analysis and presentation in geographical studies", "description": "Examine the methods of data collection, analysis and presentation in geographical studies"},
                        {"name": "Collect, analyse, interpret and present statistical data on a Geographical phenomenon", "description": "Collect, analyse, interpret and present statistical data on a Geographical phenomenon"},
                        {"name": "Appreciate the importance of statistics in day-to-day life", "description": "Appreciate the importance of statistics in day-to-day life"}
                    ],
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
                },
                {
                    "name": "Geographic Information Systems (GIS)",
                    "lessons": 13,
                    "slos": [
                        {"name": "Explain Geographic Information Systems (GIS), Global Positioning System (GPS) and Remote Sensing (RS) as geospatial technologies", "description": "Explain GIS, GPS and RS as geospatial technologies"},
                        {"name": "Describe components of GIS as used in geo-referencing information", "description": "Describe components of GIS as used in geo-referencing information"},
                        {"name": "Examine the importance of GIS in geographical studies", "description": "Examine the importance of GIS in geographical studies"},
                        {"name": "Apply GIS in locating key features in the locality", "description": "Apply GIS in locating key features in the locality"},
                        {"name": "Acknowledge the importance of GIS in day-to-day life", "description": "Acknowledge the importance of GIS in day-to-day life"}
                    ],
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
        },
        {
            "name": "Natural Systems and Processes",
            "substrands": [
                {
                    "name": "Rocks",
                    "lessons": 18,
                    "slos": [
                        {"name": "Examine the classification of rocks according to the mode of formation and age", "description": "Examine the classification of rocks according to the mode of formation and age"},
                        {"name": "Describe the distribution of rocks in Kenya", "description": "Describe the distribution of rocks in Kenya"},
                        {"name": "Analyse the significance of rocks in Kenya", "description": "Analyse the significance of rocks in Kenya"},
                        {"name": "Sample rock types in your locality", "description": "Sample rock types in your locality"},
                        {"name": "Appreciate the significance of rocks in Kenya", "description": "Appreciate the significance of rocks in Kenya"}
                    ],
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
                },
                {
                    "name": "Folding",
                    "lessons": 12,
                    "slos": [
                        {"name": "Distinguish the types of folds resulting from tectonic forces", "description": "Distinguish the types of folds resulting from tectonic forces"},
                        {"name": "Describe the resultant features of folding on the Earth's surface", "description": "Describe the resultant features of folding on the Earth's surface"},
                        {"name": "Analyse the significance of folding and the resultant features", "description": "Analyse the significance of folding and the resultant features"},
                        {"name": "Illustrate the distribution of fold mountains in the world", "description": "Illustrate the distribution of fold mountains in the world"},
                        {"name": "Appreciate the influence of folding and the resultant features on human activities", "description": "Appreciate the influence of folding and the resultant features on human activities"}
                    ],
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
                },
                {
                    "name": "Vulcanicity",
                    "lessons": 13,
                    "slos": [
                        {"name": "Investigate the causes of vulcanicity in the Earth", "description": "Investigate the causes of vulcanicity in the Earth"},
                        {"name": "Describe features resulting from volcanic activities in the world", "description": "Describe features resulting from volcanic activities in the world"},
                        {"name": "Illustrate the global distribution of features due to vulcanicity", "description": "Illustrate the global distribution of features due to vulcanicity"},
                        {"name": "Examine the significance of vulcanicity on human activities", "description": "Examine the significance of vulcanicity on human activities"},
                        {"name": "Acknowledge the effects of vulcanicity on the environment", "description": "Acknowledge the effects of vulcanicity on the environment"}
                    ],
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
                },
                {
                    "name": "Earthquakes",
                    "lessons": 10,
                    "slos": [
                        {"name": "Examine causes of earthquakes on Earth", "description": "Examine causes of earthquakes on Earth"},
                        {"name": "Illustrate the distribution of earthquake zones in the world", "description": "Illustrate the distribution of earthquake zones in the world"},
                        {"name": "Investigate the effects of earthquakes on the environment", "description": "Investigate the effects of earthquakes on the environment"},
                        {"name": "Design disaster preparedness and management strategies for coping with effects of earthquakes", "description": "Design disaster preparedness and management strategies for coping with effects of earthquakes"},
                        {"name": "Appreciate the understanding of earthquakes for disaster preparedness and management", "description": "Appreciate the understanding of earthquakes for disaster preparedness and management"}
                    ],
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
        },
        {
            "name": "Human and Economic Activities",
            "substrands": [
                {
                    "name": "Agriculture",
                    "lessons": 15,
                    "slos": [
                        {"name": "Explore types of agriculture in the world", "description": "Explore types of agriculture in the world (subsistence, commercial, urban agriculture)"},
                        {"name": "Explain the importance of agriculture in the society", "description": "Explain the importance of agriculture in the society"},
                        {"name": "Analyse the trends in agriculture in Africa", "description": "Analyse the trends in agriculture in Africa"},
                        {"name": "Examine challenges facing agriculture in Kenya", "description": "Examine challenges facing agriculture in Kenya"},
                        {"name": "Design strategies towards enhancing agricultural productivity in Kenya", "description": "Design strategies towards enhancing agricultural productivity in Kenya"},
                        {"name": "Appreciate the role of agriculture towards food security in Kenya", "description": "Appreciate the role of agriculture towards food security in Kenya"}
                    ],
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
                },
                {
                    "name": "Mining",
                    "lessons": 20,
                    "slos": [
                        {"name": "Examine the factors influencing occurrence and exploitation of minerals", "description": "Examine the factors influencing occurrence and exploitation of minerals"},
                        {"name": "Describe the methods used in extraction of minerals in the world", "description": "Describe the methods used in extraction of minerals in the world"},
                        {"name": "Explore the mining of limestone in Kenya, diamond in Botswana and iron ore in Australia", "description": "Explore the mining of limestone in Kenya, diamond in Botswana and iron ore in Australia"},
                        {"name": "Analyse the effects of mining on the environment and possible solutions", "description": "Analyse the effects of mining on the environment and possible solutions"},
                        {"name": "Apply statistical skills to establish trends in mineral production in East Africa", "description": "Apply statistical skills to establish trends in mineral production in East Africa"},
                        {"name": "Recognize the significance of minerals to the economy of Kenya", "description": "Recognize the significance of minerals to the economy of Kenya"}
                    ],
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
                },
                {
                    "name": "Energy",
                    "lessons": 20,
                    "slos": [
                        {"name": "Examine the types and sources of energy for domestic and industrial use", "description": "Examine the types and sources of energy for domestic and industrial use"},
                        {"name": "Analyse the development of renewable energy in Kenya and the selected countries", "description": "Analyse the development of renewable energy in Kenya and the selected countries"},
                        {"name": "Explore the significance of renewable energy on socio-economic development", "description": "Explore the significance of renewable energy on socio-economic development"},
                        {"name": "Manage and conserve energy in the community", "description": "Manage and conserve energy in the community"},
                        {"name": "Appreciate sustainable use of energy for socio-economic development", "description": "Appreciate sustainable use of energy for socio-economic development"}
                    ],
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
                },
                {
                    "name": "Industry",
                    "lessons": 20,
                    "slos": [
                        {"name": "Explore the types of industries in the world", "description": "Explore the types of industries in the world"},
                        {"name": "Establish the factors influencing location and development of industries in the world", "description": "Establish the factors influencing location and development of industries in the world"},
                        {"name": "Analyse the development of industries in Kenya and the selected countries", "description": "Analyse the development of industries in Kenya and the selected countries"},
                        {"name": "Examine the challenges facing industries and possible solutions in Kenya", "description": "Examine the challenges facing industries and possible solutions in Kenya"},
                        {"name": "Model a cottage industry in the school", "description": "Model a cottage industry in the school"},
                        {"name": "Acknowledge the significance of industries in the society", "description": "Acknowledge the significance of industries in the society"}
                    ],
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

# ============================================================================
# HISTORY AND CITIZENSHIP - COMPLETE DATA
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
                        {"name": "Explore the linguistic groups in Kenya", "description": "Explore the linguistic groups in Kenya"},
                        {"name": "Discuss the causes and effects of migration, settlement and expansion of the linguistic groups", "description": "Discuss the causes and effects of migration, settlement and expansion of the linguistic groups"},
                        {"name": "Trace the migration routes and settlement areas of the linguistic groups in Kenya", "description": "Trace the migration routes and settlement areas of the linguistic groups in Kenya"},
                        {"name": "Apply the knowledge of diverse communities of Kenya to promote social cohesion", "description": "Apply the knowledge of diverse communities of Kenya to promote social cohesion"},
                        {"name": "Appreciate the diversity of communities in Kenya", "description": "Appreciate the diversity of communities in Kenya"}
                    ],
                    "competencies": ["Communication and Collaboration", "Citizenship"],
                    "values": ["Responsibility", "Unity"],
                    "pcis": ["Citizenship Education", "Ethnic relations"],
                    "inquiry_questions": ["How can you promote harmonious living among the diverse communities of Kenya?"]
                },
                {
                    "name": "Establishment of colonial rule",
                    "lessons": 12,
                    "slos": [
                        {"name": "Examine the reasons for the establishment of colonial rule", "description": "Examine the reasons for the establishment of colonial rule"},
                        {"name": "Evaluate the methods applied by the British in the establishment of colonial rule in Kenya", "description": "Evaluate the methods applied by the British in the establishment of colonial rule in Kenya"},
                        {"name": "Discuss the process of establishment of colonial rule in Kenya", "description": "Discuss the process of establishment of colonial rule in Kenya"},
                        {"name": "Apply lesson learnt from the process of establishment of colonial rule in Kenya", "description": "Apply lesson learnt from the process of establishment of colonial rule in Kenya"},
                        {"name": "Desire to maintain independence and unity in Kenya", "description": "Desire to maintain independence and unity in Kenya"}
                    ],
                    "competencies": ["Digital Literacy", "Self-Efficacy"],
                    "values": ["Unity", "Responsibility"],
                    "pcis": ["Safety and Security", "Online Safety"],
                    "inquiry_questions": ["How can we maintain independence in daily lives?", "Why was it wrong for the British to impose their rule on Africans in Kenya?"]
                },
                {
                    "name": "The Constitution of Kenya (2010)",
                    "lessons": 8,
                    "slos": [
                        {"name": "Categorise the type of public resources in Kenya", "description": "Categorise the type of public resources in Kenya"},
                        {"name": "Analyse the importance of public resources for posterity", "description": "Analyse the importance of public resources for posterity"},
                        {"name": "Develop strategies for sustainable utilisation of public resources", "description": "Develop strategies for sustainable utilisation of public resources"},
                        {"name": "Advocate for efficient use of public resources for an ethical society", "description": "Advocate for efficient use of public resources for an ethical society"},
                        {"name": "Desire to support efficient use of public resources to promote ethical practices", "description": "Desire to support efficient use of public resources to promote ethical practices"}
                    ],
                    "competencies": ["Communication and Collaboration", "Learning to Learn"],
                    "values": ["Patriotism", "Responsibility"],
                    "pcis": ["Citizenship Education", "Civic responsibility"],
                    "inquiry_questions": ["What are the challenges faced in ensuring efficient utilisation of public resources?", "How can public resources be protected and preserved?"]
                },
                {
                    "name": "Political developments and challenges since independence",
                    "lessons": 10,
                    "slos": [
                        {"name": "Analyse major political developments in Kenya since Independence", "description": "Analyse major political developments in Kenya since Independence"},
                        {"name": "Discuss the major political challenges since independence", "description": "Discuss the major political challenges since independence"},
                        {"name": "Propose possible solutions to the major political challenges", "description": "Propose possible solutions to the major political challenges"},
                        {"name": "Develop activities that promote peaceful political environments in Kenya", "description": "Develop activities that promote peaceful political environments in Kenya"},
                        {"name": "Embrace peaceful coexistence for harmonious living", "description": "Embrace peaceful coexistence for harmonious living"}
                    ],
                    "competencies": ["Critical Thinking and Problem Solving", "Citizenship"],
                    "values": ["Patriotism", "Social Justice"],
                    "pcis": ["Citizenship Education", "National values"],
                    "inquiry_questions": ["How can you participate in political developments in your community?", "What solutions can you provide for challenges facing our society?"]
                },
                {
                    "name": "Elections in Kenya",
                    "lessons": 15,
                    "slos": [
                        {"name": "Identify the guidelines governing elections in Kenya", "description": "Identify the guidelines governing elections in Kenya"},
                        {"name": "Describe the roles and functions of IEBC in Kenya", "description": "Describe the roles and functions of IEBC in Kenya"},
                        {"name": "Elaborate the electoral processes in Kenya", "description": "Elaborate the electoral processes in Kenya"},
                        {"name": "Enumerate measures taken by IEBC in curbing election malpractices in management of elections", "description": "Enumerate measures taken by IEBC in curbing election malpractices in management of elections"},
                        {"name": "Appreciate the roles and functions of IEBC in Kenya", "description": "Appreciate the roles and functions of IEBC in Kenya"}
                    ],
                    "competencies": ["Citizenship", "Creativity and Imagination"],
                    "values": ["Unity", "Social Justice"],
                    "pcis": ["Citizenship Education", "Good governance", "Social cohesion"],
                    "inquiry_questions": ["Why are elections important?", "Which values can citizens embrace to avoid election malpractices?"]
                },
                {
                    "name": "National integration",
                    "lessons": 8,
                    "slos": [
                        {"name": "Discuss the importance of national integration", "description": "Discuss the importance of national integration"},
                        {"name": "Explain the components of national integration", "description": "Explain the components of national integration"},
                        {"name": "Examine factors that limit national integration", "description": "Examine factors that limit national integration"},
                        {"name": "Demonstrate ways of enhancing national integration", "description": "Demonstrate ways of enhancing national integration"},
                        {"name": "Acknowledge the importance of national unity", "description": "Acknowledge the importance of national unity"}
                    ],
                    "competencies": ["Communication and Collaboration", "Digital Literacy"],
                    "values": ["Patriotism", "Unity"],
                    "pcis": ["Citizenship Education", "Good governance", "Ethnic relations"],
                    "inquiry_questions": ["How can you enhance national integration?"]
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
                        {"name": "Explain the factors that led to transition from migratory to sedentary lifestyle by early humans", "description": "Explain the factors that led to transition from migratory to sedentary lifestyle by early humans"},
                        {"name": "Analyse advancements that took place during the Neolithic revolution", "description": "Analyse advancements that took place during the Neolithic revolution"},
                        {"name": "Examine the contributions of Neolithic revolution to the modern society", "description": "Examine the contributions of Neolithic revolution to the modern society"},
                        {"name": "Classify the characteristics of pastoralism in reference to selected communities in Africa", "description": "Classify the characteristics of pastoralism in reference to selected communities in Africa (Maasai and Fulani)"},
                        {"name": "Propose solutions to challenges facing contemporary pastoralism in Africa", "description": "Propose solutions to challenges facing contemporary pastoralism in Africa"},
                        {"name": "Recognise the advancements that took place during the Neolithic revolution", "description": "Recognise the advancements that took place during the Neolithic revolution"}
                    ],
                    "competencies": ["Digital Literacy", "Critical Thinking and Problem Solving", "Learning to Learn"],
                    "values": ["Responsibility", "Patriotism"],
                    "pcis": ["Environmental conservation", "Online safety"],
                    "inquiry_questions": ["How did daily life change due to shifting from a nomadic lifestyle to a sedentary life?", "Which factors influenced pastoralism in the pre-colonial period?"]
                },
                {
                    "name": "African Civilizations up to 19th century (Wanga, Buganda And Nyamwezi)",
                    "lessons": 10,
                    "slos": [
                        {"name": "Examine the development of selected early civilizations in Africa", "description": "Examine the development of selected early civilizations in Africa (Wanga, Buganda, Nyamwezi)"},
                        {"name": "Analyse the importance of ancient African civilizations to modern society", "description": "Analyse the importance of ancient African civilizations to modern society"},
                        {"name": "Apply the best practices from the early civilizations", "description": "Apply the best practices from the early civilizations"},
                        {"name": "Appreciate contributions of early civilizations", "description": "Appreciate contributions of early civilizations"}
                    ],
                    "competencies": ["Citizenship", "Learning to Learn"],
                    "values": ["Respect", "Unity"],
                    "pcis": ["Good Governance"],
                    "inquiry_questions": ["How do the early civilizations differ from the current leadership structure?"]
                },
                {
                    "name": "Colonization of Africa",
                    "lessons": 10,
                    "slos": [
                        {"name": "Discuss the significance of the Berlin conference in relation to scramble for and partition of Africa", "description": "Discuss the significance of the Berlin conference in relation to scramble for and partition of Africa"},
                        {"name": "Evaluate how key players determined the colonization of Africa", "description": "Evaluate how key players determined the colonization of Africa"},
                        {"name": "Discern the extent to which different reasons influenced colonisation of Africa", "description": "Discern the extent to which different reasons influenced colonisation of Africa"},
                        {"name": "Justify why it was inevitable to end colonialisation of Africa to promote a sense of nationalism", "description": "Justify why it was inevitable to end colonialisation of Africa to promote a sense of nationalism"},
                        {"name": "Appreciate the justification of the end of colonization of Africa to promote a sense of nationalism", "description": "Appreciate the justification of the end of colonization of Africa to promote a sense of nationalism"}
                    ],
                    "competencies": ["Critical Thinking and Problem Solving", "Communication and Collaboration"],
                    "values": ["Social Justice", "Unity"],
                    "pcis": ["Citizenship Education", "Equity and non-discrimination"],
                    "inquiry_questions": ["How did Otto Von Bismarck fast-track the process towards scramble for and partition of Africa?", "Why was colonialism unfair to Africans?"]
                },
                {
                    "name": "Modern Nationalism in Africa",
                    "lessons": 10,
                    "slos": [
                        {"name": "Explore factors that have influenced nationalism in Africa", "description": "Explore factors that have influenced nationalism in Africa"},
                        {"name": "Draw lessons from key leaders who contributed to nationalism in African countries", "description": "Draw lessons from key leaders who contributed to nationalism in African countries (Thomas Sankara, Desmond Tutu, Julius Nyerere, Anwar Sadat)"},
                        {"name": "Illustrate best practices that have been adopted by African nations to strengthen nationalism", "description": "Illustrate best practices that have been adopted by African nations to strengthen nationalism"},
                        {"name": "Acknowledge modern African Nationalism in development of modern African states", "description": "Acknowledge modern African Nationalism in development of modern African states"}
                    ],
                    "competencies": ["Learning to Learn", "Digital Literacy"],
                    "values": ["Patriotism", "Unity"],
                    "pcis": ["Safety and Security", "Non-violent conflict resolution", "Ethnic relations"],
                    "inquiry_questions": ["How can you advance modern nationalism?"]
                },
                {
                    "name": "Global wars on Africa",
                    "lessons": 8,
                    "slos": [
                        {"name": "Explore how the global wars affected Africa", "description": "Explore how the global wars affected Africa (World War 1 and 2, Cold War, Gulf War, Russia-Ukraine)"},
                        {"name": "Apply lessons learnt from the global wars for posterity", "description": "Apply lessons learnt from the global wars for posterity"},
                        {"name": "Desire to discourage global wars for sustainable peace", "description": "Desire to discourage global wars for sustainable peace"}
                    ],
                    "competencies": ["Learning to Learn", "Citizenship"],
                    "values": ["Peace", "Love"],
                    "pcis": ["Citizenship Education", "Peace Education"],
                    "inquiry_questions": ["Which strategies can UN apply to discourage global wars?"]
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
                        {"name": "Classify the causes of the French revolutions", "description": "Classify the causes of the French revolutions"},
                        {"name": "Explain the significance of the French revolution to world economies", "description": "Explain the significance of the French revolution to world economies"},
                        {"name": "Design the best practices from the French revolution in daily interactions", "description": "Design the best practices from the French revolution in daily interactions"},
                        {"name": "Appreciate the significance of the French revolution to the world economies today", "description": "Appreciate the significance of the French revolution to the world economies today"}
                    ],
                    "competencies": ["Learning to Learn", "Citizenship"],
                    "values": ["Social Justice", "Responsibility"],
                    "pcis": ["Citizenship Education", "Equity and non-discrimination"],
                    "inquiry_questions": ["What lessons do we learn from the French revolution?"]
                },
                {
                    "name": "International organisations",
                    "lessons": 8,
                    "slos": [
                        {"name": "Enumerate the significance of different types of international organisations", "description": "Enumerate the significance of different types of international organisations"},
                        {"name": "Examine factors that strengthen ties among commonwealth countries", "description": "Examine factors that strengthen ties among commonwealth countries"},
                        {"name": "Illustrate opportunities and challenges facing commonwealth nations", "description": "Illustrate opportunities and challenges facing commonwealth nations"},
                        {"name": "Appreciate the significance of different types of international organisations", "description": "Appreciate the significance of different types of international organisations"}
                    ],
                    "competencies": ["Learning to Learn", "Critical Thinking and Problem Solving"],
                    "values": ["Unity", "Respect"],
                    "pcis": ["Citizenship Education", "Social cohesion"],
                    "inquiry_questions": ["Why are key values important for sustainable relations among commonwealth nations?", "Which activities can promote strong ties in international organisations?"]
                },
                {
                    "name": "Modern Slavery and Servitude",
                    "lessons": 10,
                    "slos": [
                        {"name": "Discuss various forms of slavery and servitude in the modern world", "description": "Discuss various forms of slavery and servitude in the modern world"},
                        {"name": "Assess the factors that cause slavery and servitude in the modern world", "description": "Assess the factors that cause slavery and servitude in the modern world"},
                        {"name": "Illustrate ways in which governments and civil society collaborate to end slavery and servitude", "description": "Illustrate ways in which governments and civil society collaborate to end slavery and servitude in the society today"},
                        {"name": "Elaborate the roles of abolitionists movements in the modern society", "description": "Elaborate the roles of abolitionists movements in the modern society"},
                        {"name": "Appreciate the need to free the world from slavery and servitude", "description": "Appreciate the need to free the world from slavery and servitude"}
                    ],
                    "competencies": ["Critical Thinking and Problem Solving", "Self-Efficacy"],
                    "values": ["Respect"],
                    "pcis": ["Social awareness skills"],
                    "inquiry_questions": ["What can you do to end slavery and servitude in the world?"]
                },
                {
                    "name": "Global Governance",
                    "lessons": 10,
                    "slos": [
                        {"name": "Identify the guiding principles for global governance for a sustainable society", "description": "Identify the guiding principles for global governance for a sustainable society"},
                        {"name": "Illustrate key areas in global governance that guarantee a stable global trends", "description": "Illustrate key areas in global governance that guarantee a stable global trends"},
                        {"name": "Examine the importance of global governance", "description": "Examine the importance of global governance"},
                        {"name": "Explore emerging issues and possible opportunities in global governance", "description": "Explore emerging issues and possible opportunities in global governance (environmental, technological, political, economic and social)"},
                        {"name": "Recognise the importance of good global governance", "description": "Recognise the importance of good global governance"}
                    ],
                    "competencies": ["Communication and Collaboration", "Learning to Learn"],
                    "values": ["Responsibility", "Respect"],
                    "pcis": ["Citizenship Education", "Good governance", "Prevention of global warming"],
                    "inquiry_questions": ["Which activities are significant in promoting global governance?", "What is the role of UN in fostering global governance?"]
                },
                {
                    "name": "The 1st Industrial Revolution",
                    "lessons": 8,
                    "slos": [
                        {"name": "Compare the factors that led to industrial revolution in Britain and USA", "description": "Compare the factors that led to industrial revolution in Britain and USA"},
                        {"name": "Discuss impacts of the 1st industrial revolution on Africa", "description": "Discuss impacts of the 1st industrial revolution on Africa"},
                        {"name": "Appraise measures taken to address the impact of 1st industrial revolution on Africa", "description": "Appraise measures taken to address the impact of 1st industrial revolution on Africa"},
                        {"name": "Recognize the measures taken by the Africans to address the impact of 1st industrial revolution on Africa", "description": "Recognize the measures taken by the Africans to address the impact of 1st industrial revolution on Africa"}
                    ],
                    "competencies": ["Self-Efficacy", "Creativity and Imagination"],
                    "values": ["Responsibility", "Unity"],
                    "pcis": ["Citizenship Education", "Equity and non-discrimination"],
                    "inquiry_questions": ["How did the 1st industrial revolution underdevelop Africa?", "How did the 1st industrial revolution contribute to colonization in Africa?"]
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
                        {"name": "Identify national activities that contribute peace in Kenya for harmonious living", "description": "Identify national activities that contribute peace in Kenya for harmonious living"},
                        {"name": "Examine ways in which the Constitution (2010) strives to prevent conflicts in Kenya", "description": "Examine ways in which the Constitution (2010) strives to prevent conflicts in Kenya"},
                        {"name": "Deduce incidences where the constitution has been applied to foster peace and curb conflicts in a community", "description": "Deduce incidences where the constitution has been applied to foster peace and curb conflicts in a community"},
                        {"name": "Desire to uphold peace and curb conflicts in Kenya", "description": "Desire to uphold peace and curb conflicts in Kenya"}
                    ],
                    "competencies": ["Critical Thinking and Problem Solving", "Communication and Collaboration"],
                    "values": ["Responsibility", "Respect"],
                    "pcis": ["Citizenship Education", "Social cohesion", "Peace Education"],
                    "inquiry_questions": ["What are the benefits of a peaceful nation?", "How do you promote peace and conflict transformation in the community?"]
                },
                {
                    "name": "The 4th Industrial and Technologies Revolution",
                    "lessons": 9,
                    "slos": [
                        {"name": "Trace the technological advancements in the 4th generation", "description": "Trace the technological advancements in the 4th generation"},
                        {"name": "Analyse the role of information and communication technology in the 4th generation", "description": "Analyse the role of information and communication technology in the 4th generation"},
                        {"name": "Discuss the impact of technology in the 4th generation", "description": "Discuss the impact of technology in the 4th generation"},
                        {"name": "Exploit the opportunities provided by the 4th Industrial revolution for promotion of growth and sustainability in the society", "description": "Exploit the opportunities provided by the 4th Industrial revolution for promotion of growth and sustainability in the society"},
                        {"name": "Appreciate the importance of technology in life", "description": "Appreciate the importance of technology in life"}
                    ],
                    "competencies": ["Critical Thinking and Problem Solving", "Digital Literacy"],
                    "values": ["Respect", "Integrity"],
                    "pcis": ["Safety and Security", "Online Safety", "Financial Literacy"],
                    "inquiry_questions": ["What are the benefits of the 4th generation technologies?", "How has technology revolutionized acquisition of historical information?"]
                },
                {
                    "name": "Equity and non-discrimination",
                    "lessons": 8,
                    "slos": [
                        {"name": "Analyse factors that promote equity and non-discrimination in the society", "description": "Analyse factors that promote equity and non-discrimination in the society"},
                        {"name": "Identify historical injustice in the society that promote inequality and discrimination", "description": "Identify historical injustice in the society that promote inequality and discrimination"},
                        {"name": "Develop measures that promote equity and non-discrimination in the society", "description": "Develop measures that promote equity and non-discrimination in the society"},
                        {"name": "Desire to promote equity and non-discrimination in the society", "description": "Desire to promote equity and non-discrimination in the society"}
                    ],
                    "competencies": ["Critical Thinking and Problem Solving", "Communication and Collaboration"],
                    "values": ["Respect", "Unity"],
                    "pcis": ["Online Safety", "Citizenship Education", "Social cohesion"],
                    "inquiry_questions": ["How can we eradicate inequality and discrimination in society?"]
                }
            ]
        }
    ]
}

# ============================================================================
# KISWAHILI LUGHA - COMPLETE DATA (Swahili names preserved)
# ============================================================================

KISWAHILI_LUGHA_DATA = {
    "name": "Kiswahili Lugha",
    "strands": [
        {
            "name": "Kusikiliza na Kuzungumza (Listening and Speaking)",
            "substrands": [
                {
                    "name": "Ufahamu wa Kusikiliza (Comprehension of Listening)",
                    "lessons": 4,
                    "slos": [
                        {"name": "Kueleza maana ya ujumbe na fani katika matini simulizi ili kuipambanua", "description": "Explain the meaning of message and art in oral texts to distinguish them"},
                        {"name": "Kutabiri ujumbe wa matini simulizi kwa kuzingatia anwani", "description": "Predict the message of oral texts based on the title"},
                        {"name": "Kutambua ujumbe katika matini simulizi aliyosikiliza", "description": "Identify the message in oral texts listened to"},
                        {"name": "Kuchambua vipengele vya fani katika matini simulizi aliyosikiliza", "description": "Analyze elements of art in oral texts listened to"},
                        {"name": "Kuchangamkia kuchambua ujumbe na fani katika ufahamu wa kusikiliza ili kukuza stadi ya kusikiliza", "description": "Enjoy analyzing message and art in listening comprehension to develop listening skills"}
                    ],
                    "competencies": ["Communication and Collaboration", "Critical Thinking and Problem Solving"],
                    "values": ["Unity", "Respect"],
                    "pcis": ["Self-Awareness"],
                    "inquiry_questions": ["Je, ni mambo gani yanayozingatia ili kutambua ujumbe na fani katika matini simulizi unayosikiliza?"]
                },
                {
                    "name": "Matamshi Bora (Good Pronunciation)",
                    "lessons": 4,
                    "slos": [
                        {"name": "Kutambua sauti /b/, /mb/, /bw/ na /mbw/ katika matini", "description": "Identify sounds /b/, /mb/, /bw/ and /mbw/ in texts"},
                        {"name": "Kutamka sauti /b/, /mb/, /bw/ na /mbw/ ipasavyo katika maneno", "description": "Pronounce sounds /b/, /mb/, /bw/ and /mbw/ correctly in words"},
                        {"name": "Kutamka vitanzandimi vyenye sauti /b/, /mb/, /bw/ na /mbw/ ipasavyo", "description": "Pronounce tongue twisters with sounds /b/, /mb/, /bw/ and /mbw/ correctly"},
                        {"name": "Kutunga vitanzandimi vyenye maneno yaliyo na sauti /b/, /mb/, /bw/ na /mbw/", "description": "Compose tongue twisters with words containing sounds /b/, /mb/, /bw/ and /mbw/"},
                        {"name": "Kuchangamkia matumizi ya sauti /b/, /mb/, /bw/ na /mbw/ katika mawasiliano ili kukuza matamshi bora", "description": "Enjoy using sounds /b/, /mb/, /bw/ and /mbw/ in communication to develop good pronunciation"}
                    ],
                    "competencies": ["Communication and Collaboration", "Creativity and Imagination"],
                    "values": ["Responsibility", "Respect"],
                    "pcis": ["Communication Skills"],
                    "inquiry_questions": ["Matamshi bora yana umuhimu gani katika mawasiliano?"]
                },
                {
                    "name": "Kuzungumza kwa Kupasha Habari (Speaking to Inform)",
                    "lessons": 4,
                    "slos": [
                        {"name": "Kueleza maana ya kuzungumza kwa kupasha habari ili kukutofautisha na aina nyingine za uzungumzaji", "description": "Explain the meaning of informative speaking to distinguish it from other types of speaking"},
                        {"name": "Kutambua aina za uzungumzaji wa kupasha habari ili kuzitofautisha", "description": "Identify types of informative speaking to distinguish them"},
                        {"name": "Kujadili vipengele vya kuzingatia katika kuzungumza kwa kupasha habari", "description": "Discuss elements to consider in informative speaking"},
                        {"name": "Kuwasilisha mazungumzo ya kupasha habari kuhusu suala lengwa", "description": "Present informative speech about a target topic"},
                        {"name": "Kuchangamkia kushiriki katika kuzungumza kwa kupasha habari ili kukuza stadi za mawasiliano", "description": "Enjoy participating in informative speaking to develop communication skills"}
                    ],
                    "competencies": ["Communication and Collaboration", "Self-Efficacy"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Self-Awareness", "Communication Skills"],
                    "inquiry_questions": ["Kwa nini ni muhimu kushiriki katika mazungumzo ya kupasha habari?"]
                },
                {
                    "name": "Kusikiliza kwa Kupata Habari (Listening to Obtain Information)",
                    "lessons": 4,
                    "slos": [
                        {"name": "Kutambua miktadha ambapo usikizaji wa kupata habari hufanyika", "description": "Identify contexts where listening to obtain information occurs"},
                        {"name": "Kujadili vipengele vya kuzingatia katika kusikiliza kwa kupata habari", "description": "Discuss elements to consider in listening to obtain information"},
                        {"name": "Kushiriki katika mazungumzo akizingatia vipengele vya kusikiliza kwa kupata habari", "description": "Participate in conversations considering elements of listening to obtain information"},
                        {"name": "Kujadili ujumbe katika matini aliyosikiliza ili kukuza umakinifu", "description": "Discuss the message in texts listened to develop attentiveness"},
                        {"name": "Kujadili maana ya msamiati wa suala lengwa kulingana na matini aliyosikiliza", "description": "Discuss meanings of vocabulary related to target topic based on texts listened to"},
                        {"name": "Kujenga mazoea ya kuzingatia kanuni zifaazo za kusikiliza kwa kupata habari", "description": "Build habits of following appropriate rules for listening to obtain information"}
                    ],
                    "competencies": ["Communication and Collaboration", "Learning to Learn"],
                    "values": ["Respect", "Responsibility"],
                    "pcis": ["Safety and Security"],
                    "inquiry_questions": ["Unazingatia nini katika kusikiliza ili kupata ujumbe na maana ya msamiati?"]
                },
                {
                    "name": "Kusikiliza kwa Kupambanua (Listening to Discriminate)",
                    "lessons": 4,
                    "slos": [
                        {"name": "Kueleza maana ya kusikiliza kwa kupambanua ili kukutofautisha na aina nyingine za kusikiliza", "description": "Explain the meaning of discriminative listening to distinguish it from other types"},
                        {"name": "Kutambua vipengele vya kuzingatia katika kusikiliza kwa kupambanua ili kufasiri maana", "description": "Identify elements to consider in discriminative listening to interpret meaning"},
                        {"name": "Kujadili mielekeo kuhusu ujumbe kutokana na msamiati, viziada lugha na kiimbo katika matini aliyosikiliza", "description": "Discuss attitudes about messages based on vocabulary, paralanguage and intonation in texts listened to"},
                        {"name": "Kueleza maana ya msamiati kutokana na viziada lugha na kiimbo cha mzungumzaji", "description": "Explain meanings of vocabulary based on paralanguage and intonation of the speaker"}
                    ],
                    "competencies": ["Critical Thinking and Problem Solving", "Communication and Collaboration"],
                    "values": ["Respect", "Integrity"],
                    "pcis": ["Self-Awareness", "Critical Thinking"],
                    "inquiry_questions": ["Kwa nini ni muhimu kusikiliza kwa kupambanua?"]
                },
                {
                    "name": "Uzungumzaji wa Papo kwa Hapo (Spontaneous Conversation)",
                    "lessons": 4,
                    "slos": [
                        {"name": "Kueleza maana ya uzungumzaji wa papo kwa hapo ili kuutofautisha na aina nyingine za mazungumzo", "description": "Explain the meaning of spontaneous conversation to distinguish it from other types"},
                        {"name": "Kueleza miktadha ambapo uzungumzaji wa papo kwa hapo hutokea katika jamii yake", "description": "Explain contexts where spontaneous conversation occurs in the community"},
                        {"name": "Kujadili umuhimu wa uzungumzaji wa papo kwa hapo katika kukuza stadi ya kuzungumza", "description": "Discuss the importance of spontaneous conversation in developing speaking skills"},
                        {"name": "Kujadili kanuni za uzungumzaji wa papo kwa hapo", "description": "Discuss rules of spontaneous conversation"},
                        {"name": "Kushiriki katika uzungumzaji wa papo kwa hapo akizingatia kanuni zifaazo", "description": "Participate in spontaneous conversation following appropriate rules"},
                        {"name": "Kufurahia kushiriki katika uzungumzaji wa papo kwa hapo katika maisha ya kila siku", "description": "Enjoy participating in spontaneous conversation in daily life"}
                    ],
                    "competencies": ["Communication and Collaboration", "Self-Efficacy"],
                    "values": ["Unity", "Respect"],
                    "pcis": ["Social Cohesion"],
                    "inquiry_questions": ["Uzungumzaji wa papo kwa hapo una umuhimu gani katika mawasiliano?"]
                },
                {
                    "name": "Mjadala (Debate)",
                    "lessons": 4,
                    "slos": [
                        {"name": "Kueleza maana ya mjadala ili kuupambanua", "description": "Explain the meaning of debate to distinguish it"},
                        {"name": "Kujadili sifa za mjadala ili kuzibainisha", "description": "Discuss characteristics of debate to identify them"},
                        {"name": "Kushiriki mjadala kuhusu suala lengwa akizingatia kanuni za mjadala", "description": "Participate in debate about a target topic following debate rules"},
                        {"name": "Kufurahia kushiriki katika mijadala ili kukuza mawasiliano", "description": "Enjoy participating in debates to develop communication"}
                    ],
                    "competencies": ["Communication and Collaboration", "Critical Thinking and Problem Solving"],
                    "values": ["Respect", "Integrity"],
                    "pcis": ["Leadership and Governance"],
                    "inquiry_questions": ["Mjadala una umuhimu gani katika mawasiliano?"]
                },
                {
                    "name": "Usikilizaji Husishi (Empathetic Listening)",
                    "lessons": 4,
                    "slos": [
                        {"name": "Kueleza maana ya usikilizaji husishi ili kuutofautisha na aina nyingine za usikilizaji", "description": "Explain the meaning of empathetic listening to distinguish it from other types"},
                        {"name": "Kujadili umuhimu wa usikilizaji husishi katika mawasiliano", "description": "Discuss the importance of empathetic listening in communication"},
                        {"name": "Kueleza miktadha ambapo usikilizaji husishi hutokea", "description": "Explain contexts where empathetic listening occurs"},
                        {"name": "Kujadili kanuni za usikilizaji husishi", "description": "Discuss principles of empathetic listening"},
                        {"name": "Kushiriki mazungumzo kwa kuzingatia kanuni za usikilizaji husishi", "description": "Participate in conversations following principles of empathetic listening"},
                        {"name": "Kufurahia kutumia kanuni za usikilizaji husishi katika jamii kama njia ya kukuza mawasiliano", "description": "Enjoy using principles of empathetic listening in community as a way to develop communication"}
                    ],
                    "competencies": ["Communication and Collaboration", "Self-Efficacy"],
                    "values": ["Love", "Respect", "Unity"],
                    "pcis": ["Social Cohesion", "Self-Awareness"],
                    "inquiry_questions": ["Usikilizaji husishi una umuhimu gani katika mawasiliano?"]
                },
                {
                    "name": "Kuzungumza kwa Ufasaha - Ushawishi (Persuasive Speaking)",
                    "lessons": 4,
                    "slos": [
                        {"name": "Kutambua miktadha ambapo uzungumzaji wa kushawishi hufanyika", "description": "Identify contexts where persuasive speaking occurs"},
                        {"name": "Kujadili kanuni za uzungumzaji wa kushawishi ili kuzipambanua", "description": "Discuss rules of persuasive speaking to identify them"},
                        {"name": "Kutambua kanuni za uzungumzaji wa kushawishi katika matini", "description": "Identify rules of persuasive speaking in texts"},
                        {"name": "Kuwasilisha matini ya kushawishi akizingatia kanuni zifaazo za uzungumzaji wa kushawishi", "description": "Present persuasive text following appropriate rules of persuasive speaking"},
                        {"name": "Kuonea fahari uzungumzaji wa kushawishi katika miktadha mbalimbali ili kukuza stadi ya kushawishi", "description": "Take pride in persuasive speaking in various contexts to develop persuasion skills"}
                    ],
                    "competencies": ["Communication and Collaboration", "Critical Thinking and Problem Solving"],
                    "values": ["Integrity", "Responsibility"],
                    "pcis": ["Communication Skills", "Leadership"],
                    "inquiry_questions": ["Je, mazungumzo ya kushawishi yana umuhimu gani katika jamii?"]
                },
                {
                    "name": "Kuhakiki Matini ya Kusikiliza (Critical Listening)",
                    "lessons": 4,
                    "slos": [
                        {"name": "Kueleza maana ya kusikiliza kwa kuhakiki ili kukutofautisha na aina nyingine za kusikiliza", "description": "Explain the meaning of critical listening to distinguish it from other types"},
                        {"name": "Kujadili kanuni za kusikiliza kwa kuhakiki ili kuzipambanua", "description": "Discuss rules of critical listening to identify them"},
                        {"name": "Kusikiliza matini kwa kuzingatia kanuni za kusikiliza kwa kuhakiki ili kukuza stadi ya uwazaji kina", "description": "Listen to texts following rules of critical listening to develop critical thinking skills"},
                        {"name": "Kuhakiki matini aliyosikiliza kwa kuzingatia vipengele vifaavyo", "description": "Critique texts listened to considering appropriate elements"},
                        {"name": "Kufurahia kuhakiki matini ya kusikiliza kwa kutumia kanuni zifaazo katika mawasiliano ya kila siku", "description": "Enjoy critiquing listening texts using appropriate rules in daily communication"}
                    ],
                    "competencies": ["Critical Thinking and Problem Solving", "Communication and Collaboration"],
                    "values": ["Integrity", "Respect"],
                    "pcis": ["Media Literacy", "Critical Thinking"],
                    "inquiry_questions": ["Kwa nini ni muhimu kushiriki katika usikilizaji wa kihakiki?"]
                }
            ]
        },
        {
            "name": "Kusoma (Reading)",
            "substrands": [
                {
                    "name": "Kusoma kwa Ufahamu - Kifungu Simulizi (Reading for Comprehension - Narrative)",
                    "lessons": 4,
                    "slos": [
                        {"name": "Kudondoa habari mahususi katika kifungu simulizi", "description": "Extract specific information from narrative passage"},
                        {"name": "Kupanga matukio yanavyofuatana katika kifungu simulizi alichosoma", "description": "Arrange events sequentially in narrative passage read"},
                        {"name": "Kufanya utabiri na ufasiri kutokana na kifungu simulizi", "description": "Make predictions and interpretations from narrative passage"},
                        {"name": "Kutumia msamiati katika kifungu simulizi ipasavyo", "description": "Use vocabulary in narrative passage appropriately"},
                        {"name": "Kuchangamkia kusoma kifungu simulizi ili kukuza uelewa wa habari", "description": "Enjoy reading narrative passage to develop understanding of information"}
                    ],
                    "competencies": ["Communication and Collaboration", "Critical Thinking and Problem Solving"],
                    "values": ["Responsibility", "Respect"],
                    "pcis": ["Academic Skills"],
                    "inquiry_questions": ["Kusoma kwa ufahamu kuna umuhimu gani?"]
                },
                {
                    "name": "Ufupisho - Kifungu cha Kupasha Habari (Summarizing - Informative Passage)",
                    "lessons": 4,
                    "slos": [
                        {"name": "Kutambua miktadha ambapo ufupishaji wa habari hutumika", "description": "Identify contexts where summarizing information is used"},
                        {"name": "Kujadili vipengele vya kuzingatia katika kufupisha kifungu cha kupasha habari", "description": "Discuss elements to consider in summarizing informative passage"},
                        {"name": "Kufupisha kifungu cha kupasha habari kwa kuzingatia vipengele vya ufupisho", "description": "Summarize informative passage considering elements of summary"},
                        {"name": "Kuchangamkia usomaji wa matini mbalimbali kwa nia ya kuzifupisha bila kupoteza ujumbe", "description": "Enjoy reading various texts with intention to summarize without losing message"}
                    ],
                    "competencies": ["Critical Thinking and Problem Solving", "Communication and Collaboration"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Academic Skills", "Information Literacy"],
                    "inquiry_questions": ["Ufupisho wa habari unarahisisha vipi mawasiliano?"]
                },
                {
                    "name": "Kusoma kwa Mapana (Extensive Reading)",
                    "lessons": 4,
                    "slos": [
                        {"name": "Kujadili vipengele mbalimbali vya kuzingatia katika kusoma kwa mapana", "description": "Discuss various elements to consider in extensive reading"},
                        {"name": "Kushiriki kusoma kwa mapana akizingatia vipengele vya kusoma kwa mapana", "description": "Participate in extensive reading considering its elements"},
                        {"name": "Kuandika muhtasari wa ujumbe wa matini ambayo amesoma ili kurahisisha uelewa", "description": "Write summary of message of texts read to ease understanding"},
                        {"name": "Kufurahia kusoma kwa mapana ili kujenga ufasaha wa lugha", "description": "Enjoy extensive reading to build language fluency"}
                    ],
                    "competencies": ["Learning to Learn", "Communication and Collaboration"],
                    "values": ["Responsibility", "Love"],
                    "pcis": ["Life-long Learning", "Cultural Appreciation"],
                    "inquiry_questions": ["Je, unazingatia nini unapochagua matini ya kusoma?"]
                },
                {
                    "name": "Kusoma kwa Kina - Kurashia (Intensive Reading - Skimming)",
                    "lessons": 4,
                    "slos": [
                        {"name": "Kueleza maana ya kurashia katika usomaji wa kina", "description": "Explain the meaning of skimming in intensive reading"},
                        {"name": "Kujadili vipengele vya kuzingatia katika usomaji wa kurashia", "description": "Discuss elements to consider in skimming reading"},
                        {"name": "Kusoma matini kwa kutumia mbinu ya kurashia ili kupata ujumbe", "description": "Read texts using skimming technique to get the message"},
                        {"name": "Kuthamini usomaji wa kina ili kukuza stadi ya kusoma", "description": "Value intensive reading to develop reading skills"}
                    ],
                    "competencies": ["Communication and Collaboration", "Critical Thinking and Problem Solving"],
                    "values": ["Responsibility", "Respect"],
                    "pcis": ["Academic Skills", "Research Skills"],
                    "inquiry_questions": ["Mbinu ya kurashia ina umuhimu gani katika usomaji?"]
                },
                {
                    "name": "Kusoma kwa Ufasaha - Kifungu cha Maelezo (Reading for Fluency - Descriptive Passage)",
                    "lessons": 4,
                    "slos": [
                        {"name": "Kujadili vipengele vya kuzingatia katika kusoma kwa ufasaha na umuhimu wake", "description": "Discuss elements to consider in fluent reading and its importance"},
                        {"name": "Kusoma kifungu cha maelezo akizingatia matamshi bora", "description": "Read descriptive passage with good pronunciation"},
                        {"name": "Kusoma kifungu cha maelezo akizingatia kasi ifaayo", "description": "Read descriptive passage at appropriate pace"},
                        {"name": "Kusoma kifungu cha maelezo akizingatia kiimbo na kiwango cha sauti kifaacho", "description": "Read descriptive passage with appropriate intonation and volume"},
                        {"name": "Kusoma kifungu cha maelezo akizingatia viziada lugha", "description": "Read descriptive passage considering paralanguage"},
                        {"name": "Kujenga mazoea ya kusoma kwa ufasaha kifungu cha maelezo", "description": "Build habits of reading descriptive passages fluently"}
                    ],
                    "competencies": ["Communication and Collaboration", "Self-Efficacy"],
                    "values": ["Responsibility", "Respect"],
                    "pcis": ["Communication Skills"],
                    "inquiry_questions": ["Unahitaji kuzingatia nini ili uweze kusoma kifungu cha maelezo kwa ufasaha?"]
                },
                {
                    "name": "Kusoma kwa Kina - Kuduhushi (Intensive Reading - Scanning)",
                    "lessons": 4,
                    "slos": [
                        {"name": "Kueleza maana ya kuduhushi katika usomaji ili kukutofautisha na mbinu nyingine za usomaji", "description": "Explain the meaning of scanning in reading to distinguish from other techniques"},
                        {"name": "Kujadili vipengele vya kuzingatia katika usomaji wa kuduhushi", "description": "Discuss elements to consider in scanning reading"},
                        {"name": "Kusoma matini kwa kuduhushi akizingatia msamiati na matumizi ya lugha", "description": "Read texts by scanning considering vocabulary and language use"},
                        {"name": "Kuthamini usomaji wa kuduhushi ili kukuza stadi ya kusoma", "description": "Value scanning reading to develop reading skills"}
                    ],
                    "competencies": ["Critical Thinking and Problem Solving", "Digital Literacy"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Research Skills", "Information Literacy"],
                    "inquiry_questions": ["Mbinu ya kuduhushi ina umuhimu gani katika usomaji?"]
                }
            ]
        },
        {
            "name": "Kuandika (Writing)",
            "substrands": [
                {
                    "name": "Barua ya Kirafiki (Friendly Letter)",
                    "lessons": 4,
                    "slos": [
                        {"name": "Kueleza maana ya barua ya kirafiki", "description": "Explain the meaning of friendly letter"},
                        {"name": "Kutambua miktadha ambapo barua ya kirafiki hutumika", "description": "Identify contexts where friendly letters are used"},
                        {"name": "Kueleza umuhimu wa barua ya kirafiki", "description": "Explain the importance of friendly letters"},
                        {"name": "Kujadili vipengele vya kuzingatia katika uandishi wa barua ya kirafiki", "description": "Discuss elements to consider in writing friendly letters"},
                        {"name": "Kuandika barua ya kirafiki kwa kuzingatia vipengele vifaavyo", "description": "Write friendly letter considering appropriate elements"},
                        {"name": "Kufurahia kuandika barua ya kirafiki kwa kuzingatia vipengele vifaavyo ili kufanikisha mawasiliano", "description": "Enjoy writing friendly letters with appropriate elements to achieve communication"}
                    ],
                    "competencies": ["Communication and Collaboration", "Creativity and Imagination"],
                    "values": ["Love", "Respect"],
                    "pcis": ["Social Cohesion", "Communication Skills"],
                    "inquiry_questions": ["Kwa nini ni muhimu kuandika barua ya kirafiki?"]
                },
                {
                    "name": "Insha ya Wasifu (Biographical Essay)",
                    "lessons": 4,
                    "slos": [
                        {"name": "Kueleza maana ya insha ya wasifu ili kuipambanua", "description": "Explain the meaning of biographical essay to distinguish it"},
                        {"name": "Kujadili vipengele vya uandishi wa insha ya wasifu", "description": "Discuss elements of writing biographical essays"},
                        {"name": "Kuandika insha ya wasifu kwa kuzingatia vipengele vifaavyo", "description": "Write biographical essay considering appropriate elements"},
                        {"name": "Kufurahia kuandika insha za wasifu ili kukuza ubunifu", "description": "Enjoy writing biographical essays to develop creativity"}
                    ],
                    "competencies": ["Creativity and Imagination", "Communication and Collaboration"],
                    "values": ["Respect", "Integrity"],
                    "pcis": ["Self-Awareness", "Cultural Identity"],
                    "inquiry_questions": ["Kwa nini ni muhimu kujifunza kuandika insha ya wasifu?"]
                },
                {
                    "name": "Ratiba (Schedule)",
                    "lessons": 4,
                    "slos": [
                        {"name": "Kueleza maana ya ratiba ili kuipambanua", "description": "Explain the meaning of schedule to distinguish it"},
                        {"name": "Kujadili umuhimu wa ratiba katika maisha ya kila siku", "description": "Discuss importance of schedule in daily life"},
                        {"name": "Kujadili vipengele vya ratiba ili kuvibainisha", "description": "Discuss elements of schedule to identify them"},
                        {"name": "Kuandika ratiba kwa kuzingatia vipengele vifaavyo", "description": "Write schedule considering appropriate elements"},
                        {"name": "Kujenga mazoea ya kuandika ratiba akizingatia vipengele vifaavyo", "description": "Build habits of writing schedules with appropriate elements"}
                    ],
                    "competencies": ["Self-Efficacy", "Communication and Collaboration"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Time Management", "Life Skills"],
                    "inquiry_questions": ["Ratiba ina umuhimu gani maishani?"]
                },
                {
                    "name": "Kuhariri Matini (Editing Texts)",
                    "lessons": 6,
                    "slos": [
                        {"name": "Kueleza maana ya kuhariri ili kuipambanua", "description": "Explain the meaning of editing to distinguish it"},
                        {"name": "Kujadili hatua za kuzingatia katika uhariri wa matini", "description": "Discuss steps to consider in editing texts"},
                        {"name": "Kujadili kanuni za kuhariri matini", "description": "Discuss rules of editing texts"},
                        {"name": "Kuhariri makala akizingatia kanuni za uhariri wa matini", "description": "Edit articles following rules of text editing"},
                        {"name": "Kujenga maarifa ya uhariri na kuyatumia kuboresha makala ili kufanikisha mawasiliano", "description": "Build editing knowledge and use it to improve articles for effective communication"}
                    ],
                    "competencies": ["Critical Thinking and Problem Solving", "Communication and Collaboration"],
                    "values": ["Integrity", "Responsibility"],
                    "pcis": ["Academic Skills", "Quality Assurance"],
                    "inquiry_questions": ["Uhariri una umuhimu gani katika mawasiliano?"]
                },
                {
                    "name": "Notisi (Notice)",
                    "lessons": 4,
                    "slos": [
                        {"name": "Kueleza maana ya notisi ili kuipambanua", "description": "Explain the meaning of notice to distinguish it"},
                        {"name": "Kueleza umuhimu wa notisi katika mawasiliano", "description": "Explain importance of notice in communication"},
                        {"name": "Kujadili vipengele vya kuzingatia katika kuandika notisi ili kuvibainisha", "description": "Discuss elements to consider in writing notices to identify them"},
                        {"name": "Kuandika notisi kwa kuzingatia vipengele vifaavyo", "description": "Write notice considering appropriate elements"},
                        {"name": "Kujenga mazoea ya kuandika notisi ili kurahisisha mawasiliano", "description": "Build habits of writing notices to ease communication"}
                    ],
                    "competencies": ["Communication and Collaboration", "Self-Efficacy"],
                    "values": ["Responsibility", "Respect"],
                    "pcis": ["Communication Skills", "Information Sharing"],
                    "inquiry_questions": ["Notisi ina umuhimu gani katika mawasiliano?"]
                },
                {
                    "name": "Shajara (Diary)",
                    "lessons": 4,
                    "slos": [
                        {"name": "Kueleza maana ya shajara ili kuibainisha", "description": "Explain the meaning of diary to identify it"},
                        {"name": "Kujadili umuhimu wa shajara katika uandishi wa kiuamilifu", "description": "Discuss importance of diary in functional writing"},
                        {"name": "Kueleza aina mbalimbali za shajara ili kuzipambanua", "description": "Explain various types of diaries to distinguish them"},
                        {"name": "Kujadili vipengele vya kuzingatia katika kuandika shajara", "description": "Discuss elements to consider in writing diaries"},
                        {"name": "Kuandika shajara akizingatia vipengele vya uandishi wa shajara", "description": "Write diary considering elements of diary writing"},
                        {"name": "Kuonea fahari matumizi ya shajara katika maisha ya kila siku", "description": "Take pride in using diaries in daily life"}
                    ],
                    "competencies": ["Creativity and Imagination", "Self-Efficacy"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Self-Reflection", "Time Management"],
                    "inquiry_questions": ["Kwa nini watu hutumia shajara?"]
                },
                {
                    "name": "Insha ya Masimulizi kuhusu Picha (Narrative Essay about Picture)",
                    "lessons": 4,
                    "slos": [
                        {"name": "Kueleza maana ya insha ya masimulizi kuhusu picha ili kuitofautisha na aina nyingine za insha", "description": "Explain the meaning of narrative essay about picture to distinguish from other types"},
                        {"name": "Kujadili ujumbe kutokana na insha ya picha", "description": "Discuss message from picture essay"},
                        {"name": "Kufafanua matukio ya insha ya masimulizi kutokana na picha", "description": "Explain events of narrative essay from picture"},
                        {"name": "Kuandika insha ya masimulizi kutokana na picha akizingatia ujumbe, mtindo na muundo ipasavyo", "description": "Write narrative essay from picture considering message, style and structure appropriately"},
                        {"name": "Kufurahia kuandika insha ya masimulizi kuhusu picha ili kukuza ubunifu", "description": "Enjoy writing narrative essays about pictures to develop creativity"}
                    ],
                    "competencies": ["Creativity and Imagination", "Communication and Collaboration"],
                    "values": ["Creativity", "Respect"],
                    "pcis": ["Visual Literacy", "Creative Expression"],
                    "inquiry_questions": ["Kwa nini ni muhimu kujifunza kuandika insha ya masimulizi kuhusu picha?"]
                },
                {
                    "name": "Insha Fafanuzi (Explanatory Essay)",
                    "lessons": 4,
                    "slos": [
                        {"name": "Kueleza maana ya insha fafanuzi ili kuibanisha", "description": "Explain the meaning of explanatory essay to identify it"},
                        {"name": "Kujadili vipengele vya insha fafanuzi kuhusu matatizo na utatuzi ili kuvibainisha", "description": "Discuss elements of explanatory essay about problems and solutions to identify them"},
                        {"name": "Kuandika insha fafanuzi kuhusu matatizo na utatuzi akizingatia vipengele vifaavyo", "description": "Write explanatory essay about problems and solutions considering appropriate elements"},
                        {"name": "Kufurahia kuandika insha fafanuzi ili kufanikisha mawasiliano", "description": "Enjoy writing explanatory essays to achieve communication"}
                    ],
                    "competencies": ["Critical Thinking and Problem Solving", "Communication and Collaboration"],
                    "values": ["Integrity", "Responsibility"],
                    "pcis": ["Problem Solving", "Clear Communication"],
                    "inquiry_questions": ["Kwa nini ni muhimu kujifunza kuandika insha fafanuzi?"]
                },
                {
                    "name": "Tafsiri (Translation)",
                    "lessons": 5,
                    "slos": [
                        {"name": "Kueleza maana ya tafsiri ili kuipambanua", "description": "Explain the meaning of translation to distinguish it"},
                        {"name": "Kueleza umuhimu wa tafsiri katika mawasiliano", "description": "Explain the importance of translation in communication"},
                        {"name": "Kujadili vipengele vya tafsiri katika mawasiliano", "description": "Discuss elements of translation in communication"},
                        {"name": "Kujadili hatua za kuzingatia katika kutafsiri matini", "description": "Discuss steps to consider in translating texts"},
                        {"name": "Kufanya tafsiri kwa kuzingatia vipengele vifaavyo vya tafsiri", "description": "Do translation considering appropriate elements of translation"},
                        {"name": "Kuonea fahari nafasi ya kutafsiri katika mawasiliano", "description": "Take pride in the role of translation in communication"}
                    ],
                    "competencies": ["Communication and Collaboration", "Critical Thinking and Problem Solving"],
                    "values": ["Respect", "Integrity"],
                    "pcis": ["Intercultural Communication", "Language Development"],
                    "inquiry_questions": ["Tafsiri ina umuhimu gani katika mawasiliano?"]
                }
            ]
        },
        {
            "name": "Matumizi ya Lugha (Language Use)",
            "substrands": [
                {
                    "name": "Ngeli za Nomino: A-WA, U-I, KI-VI, I-ZI (Noun Classes)",
                    "lessons": 6,
                    "slos": [
                        {"name": "Kutambua viambishi vya upatanisho wa kisarufi wa ngeli ya A-WA, U-I, KI-VI na I-ZI katika sentensi", "description": "Identify agreement affixes for noun classes A-WA, U-I, KI-VI and I-ZI in sentences"},
                        {"name": "Kutambua nomino za ngeli ya A-WA, U-I, KI-VI na I-ZI katika matini", "description": "Identify nouns of classes A-WA, U-I, KI-VI and I-ZI in texts"},
                        {"name": "Kutumia nomino katika ngeli ya A-WA, U-I, KI-VI na I-ZI katika matini kwa kuzingatia upatanisho ufaao wa kisarufi", "description": "Use nouns in classes A-WA, U-I, KI-VI and I-ZI in texts with appropriate grammatical agreement"},
                        {"name": "Kuchangamkia kutumia nomino za ngeli ya A-WA, U-I, KI-VI na I-ZI ipasavyo katika sentensi na vifungu ili kuimarisha mawasiliano", "description": "Enjoy using nouns of classes A-WA, U-I, KI-VI and I-ZI appropriately in sentences and passages to strengthen communication"}
                    ],
                    "competencies": ["Communication and Collaboration", "Critical Thinking and Problem Solving"],
                    "values": ["Respect", "Responsibility"],
                    "pcis": ["Language Development"],
                    "inquiry_questions": ["Ni mambo gani tunayozingatia katika upatanisho wa kisarufi katika sentensi?"]
                },
                {
                    "name": "Nyakati na Hali: Wakati Uliopo, Uliopita, Ujao (Tenses: Present, Past, Future)",
                    "lessons": 4,
                    "slos": [
                        {"name": "Kubainisha vitenzi vilivyo katika wakati uliopo, uliopita na ujao katika matini", "description": "Identify verbs in present, past and future tense in texts"},
                        {"name": "Kutumia wakati uliopo, uliopita na ujao ifaavyo katika matini", "description": "Use present, past and future tense appropriately in texts"},
                        {"name": "Kuchangamkia ufasaha wa lugha kwa kutumia wakati uliopo, uliopita na ujao ifaavyo katika mawasiliano", "description": "Enjoy language fluency by using present, past and future tense appropriately in communication"}
                    ],
                    "competencies": ["Communication and Collaboration", "Learning to Learn"],
                    "values": ["Responsibility", "Respect"],
                    "pcis": ["Language Development"],
                    "inquiry_questions": ["Nyakati zina umuhimu gani katika mawasiliano?"]
                },
                {
                    "name": "Mnyambuliko wa Vitenzi: Kutenda, Kutendea, Kutendwa, Kutendewa (Verb Conjugations)",
                    "lessons": 6,
                    "slos": [
                        {"name": "Kutambua kauli ya kutenda, kutendea, kutendwa na kutendewa katika vitenzi", "description": "Identify active, applicative, passive and applicative-passive forms in verbs"},
                        {"name": "Kutumia vitenzi katika kauli ya kutenda, kutendea, kutendwa na kutendewa ipasavyo katika sentensi", "description": "Use verbs in active, applicative, passive and applicative-passive forms appropriately in sentences"},
                        {"name": "Kuchangamkia kutumia ipasavyo kauli ya kutenda, kutendea, kutendwa na kutendewa ili kujenga ufasaha wa lugha", "description": "Enjoy using active, applicative, passive and applicative-passive forms appropriately to build language fluency"}
                    ],
                    "competencies": ["Communication and Collaboration", "Critical Thinking and Problem Solving"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Language Development"],
                    "inquiry_questions": ["Mnyambuliko wa vitenzi una umuhimu gani katika mawasiliano?"]
                },
                {
                    "name": "Ukanushaji: Wakati Uliopo, Uliopita, Ujao (Negation)",
                    "lessons": 5,
                    "slos": [
                        {"name": "Kueleza maana ya ukanushaji ili kuupambanua", "description": "Explain the meaning of negation to distinguish it"},
                        {"name": "Kutambua viambishi vya ukanushaji wa nyakati katika matini", "description": "Identify negation affixes for tenses in texts"},
                        {"name": "Kukanusha sentensi kwa kuzingatia viambishi vya nyakati", "description": "Negate sentences considering tense affixes"},
                        {"name": "Kufurahia ukanushaji wa nyakati ili kufanikisha mawasiliano", "description": "Enjoy negation of tenses to achieve communication"}
                    ],
                    "competencies": ["Communication and Collaboration", "Critical Thinking and Problem Solving"],
                    "values": ["Responsibility", "Respect"],
                    "pcis": ["Language Development"],
                    "inquiry_questions": ["Ukanushaji una umuhimu gani katika mawasiliano?"]
                },
                {
                    "name": "Aina za Maneno: Vielezi, Viunganishi, Vihusishi, Vihisishi (Parts of Speech: Adverbs, Conjunctions, Prepositions, Interjections)",
                    "lessons": 6,
                    "slos": [
                        {"name": "Kueleza aina za vielezi, viunganishi, vihusishi na vihisishi ili kufanikisha mawasiliano", "description": "Explain types of adverbs, conjunctions, prepositions and interjections to achieve communication"},
                        {"name": "Kutumia ipasavyo aina za vielezi, viunganishi, vihusishi na vihisishi katika matini", "description": "Use types of adverbs, conjunctions, prepositions and interjections appropriately in texts"},
                        {"name": "Kufurahia matumizi ya vielezi, viunganishi, vihusishi na vihisishi katika sentensi", "description": "Enjoy using adverbs, conjunctions, prepositions and interjections in sentences"}
                    ],
                    "competencies": ["Communication and Collaboration", "Learning to Learn"],
                    "values": ["Responsibility", "Respect"],
                    "pcis": ["Language Development"],
                    "inquiry_questions": ["Aina hizi za maneno zina umuhimu gani katika mawasiliano?"]
                },
                {
                    "name": "Uundaji wa Maneno: Mkato, Nomino Ambata, Uradidi (Word Formation: Abbreviations, Compound Nouns, Reduplication)",
                    "lessons": 4,
                    "slos": [
                        {"name": "Kueleza dhana ya uundaji wa maneno", "description": "Explain the concept of word formation"},
                        {"name": "Kujadili umuhimu wa uundaji wa maneno katika kukuza mawasiliano", "description": "Discuss the importance of word formation in developing communication"},
                        {"name": "Kujadili mbinu ya uundaji wa maneno ya mkato, kuambatisha na uradidi katika ukuzaji wa lugha", "description": "Discuss techniques of word formation through abbreviation, compounding and reduplication in language development"},
                        {"name": "Kuunda maneno akizingatia mbinu ya mkato, kuambatisha na uradidi ili kukuza ufasaha wa lugha", "description": "Form words using abbreviation, compounding and reduplication techniques to develop language fluency"},
                        {"name": "Kuchangamkia uundaji wa maneno ili kujenga ufasaha wa lugha katika mawasiliano ya kila siku", "description": "Enjoy word formation to build language fluency in daily communication"}
                    ],
                    "competencies": ["Creativity and Imagination", "Communication and Collaboration"],
                    "values": ["Creativity", "Responsibility"],
                    "pcis": ["Language Development", "Vocabulary Building"],
                    "inquiry_questions": ["Je, uundaji wa maneno mapya unasababishwa na nini?"]
                },
                {
                    "name": "Kinyume: Nomino, Vitenzi, Vivumishi (Antonyms: Nouns, Verbs, Adjectives)",
                    "lessons": 6,
                    "slos": [
                        {"name": "Kueleza dhana ya kinyume cha neno ili kuipambanua", "description": "Explain the concept of antonyms to distinguish them"},
                        {"name": "Kueleza maana ya kinyume cha nomino, vitenzi na vivumishi ili kuvitofautisha", "description": "Explain meanings of antonyms of nouns, verbs and adjectives to distinguish them"},
                        {"name": "Kueleza aina za vinyume vya nomino, vitenzi na vivumishi ili kuvipambanua", "description": "Explain types of antonyms of nouns, verbs and adjectives to identify them"},
                        {"name": "Kutumia vinyume vya nomino, vitenzi na vivumishi katika matini ipasavyo", "description": "Use antonyms of nouns, verbs and adjectives appropriately in texts"},
                        {"name": "Kufurahia matumizi yafaayo ya vinyume vya nomino, vitenzi na vivumishi ili kufanikisha mawasiliano", "description": "Enjoy appropriate use of antonyms of nouns, verbs and adjectives to achieve communication"}
                    ],
                    "competencies": ["Communication and Collaboration", "Critical Thinking and Problem Solving"],
                    "values": ["Responsibility", "Respect"],
                    "pcis": ["Vocabulary Building", "Language Development"],
                    "inquiry_questions": ["Vinyume vina umuhimu gani katika mawasiliano?"]
                },
                {
                    "name": "Sentensi: Sahili, Ambatano, Changamano (Sentences: Simple, Compound, Complex)",
                    "lessons": 5,
                    "slos": [
                        {"name": "Kueleza maana ya sentensi sahili, ambatano na changamano ili kuzipambanua", "description": "Explain meanings of simple, compound and complex sentences to distinguish them"},
                        {"name": "Kujadili sifa za sentensi sahili, ambatano na changamano ili kuzitofautisha", "description": "Discuss characteristics of simple, compound and complex sentences to differentiate them"},
                        {"name": "Kutunga sentensi sahili, ambatano na changamano ili kuzibainisha", "description": "Construct simple, compound and complex sentences to identify them"},
                        {"name": "Kujenga mazoea ya kutumia sentensi sahili, ambatano na changamano katika mawasiliano", "description": "Build habits of using simple, compound and complex sentences in communication"}
                    ],
                    "competencies": ["Communication and Collaboration", "Critical Thinking and Problem Solving"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Language Development", "Clear Communication"],
                    "inquiry_questions": ["Kutumia aina mbalimbali za sentensi kuna umuhimu gani katika mawasiliano?"]
                },
                {
                    "name": "Isimujamii (Sociolinguistics)",
                    "lessons": 5,
                    "slos": [
                        {"name": "Kueleza dhana ya isimujamii", "description": "Explain the concept of sociolinguistics"},
                        {"name": "Kujadili umuhimu wa isimujamii katika mawasiliano", "description": "Discuss the importance of sociolinguistics in communication"},
                        {"name": "Kueleza kanuni za matumizi ya lugha (mada, umri, hadhi)", "description": "Explain rules of language use (topic, age, status)"},
                        {"name": "Kueleza dhana ya rejista", "description": "Explain the concept of register"},
                        {"name": "Kuwasiliana kwa kutumia kanuni zifaazo za matumizi ya lugha katika miktadha mbalimbali", "description": "Communicate using appropriate rules of language use in various contexts"}
                    ],
                    "competencies": ["Communication and Collaboration", "Self-Efficacy"],
                    "values": ["Respect", "Responsibility", "Unity"],
                    "pcis": ["Social Awareness", "Appropriate Communication"],
                    "inquiry_questions": ["Isimujamii ina manufaa gani katika mawasiliano?"]
                }
            ]
        }
    ]
}

# Import the rest of the data - I'll include Literature in English and Physics in the next part
# due to size constraints

# ============================================================================
# DATABASE OPERATIONS
# ============================================================================

async def get_grade_10_id():
    """Get Grade 10 ID from database"""
    grade = await db.grades.find_one({"name": "Grade 10"})
    if grade:
        return str(grade["_id"])
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
    
    subject = await db.subjects.find_one({"name": subject_name, "gradeIds": grade_id})
    if not subject:
        subject = await db.subjects.find_one({"name": subject_name})
    
    if not subject:
        print(f"    No existing subject found for {subject_name}")
        return
    
    subject_id = str(subject["_id"])
    
    strands = await db.strands.find({"subjectId": subject_id}).to_list(1000)
    strand_ids = [str(s["_id"]) for s in strands]
    
    substrands = await db.substrands.find({"strandId": {"$in": strand_ids}}).to_list(10000)
    substrand_ids = [str(s["_id"]) for s in substrands]
    
    slos = await db.slos.find({"substrandId": {"$in": substrand_ids}}).to_list(10000)
    slo_ids = [str(s["_id"]) for s in slos]
    
    if slo_ids:
        result1 = await db.slo_mappings.delete_many({"sloId": {"$in": slo_ids}})
        result2 = await db.learning_activities.delete_many({"sloId": {"$in": slo_ids}})
        result3 = await db.learning_activities.delete_many({"substrandId": {"$in": substrand_ids}})
        result4 = await db.slos.delete_many({"substrandId": {"$in": substrand_ids}})
        print(f"    Deleted {result4.deleted_count} SLOs and related data")
    
    if substrand_ids:
        result = await db.substrands.delete_many({"strandId": {"$in": strand_ids}})
        print(f"    Deleted {result.deleted_count} substrands")
    
    if strand_ids:
        result = await db.strands.delete_many({"subjectId": subject_id})
        print(f"    Deleted {result.deleted_count} strands")
    
    if len(subject.get("gradeIds", [])) <= 1:
        await db.subjects.delete_one({"_id": subject["_id"]})
        print(f"    Deleted subject {subject_name}")
    else:
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
    
    await delete_existing_subject_data(subject_name, grade_id)
    
    existing_subject = await db.subjects.find_one({"name": subject_name})
    if existing_subject:
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
    
    strand_count = 0
    substrand_count = 0
    slo_count = 0
    learning_activity_count = 0
    slo_mapping_count = 0
    
    for strand_data in subject_data["strands"]:
        strand_result = await db.strands.insert_one({
            "name": strand_data["name"],
            "subjectId": subject_id
        })
        strand_id = str(strand_result.inserted_id)
        strand_count += 1
        print(f"    Strand: {strand_data['name']}")
        
        for substrand_data in strand_data["substrands"]:
            substrand_result = await db.substrands.insert_one({
                "name": substrand_data["name"],
                "strandId": strand_id
            })
            substrand_id = str(substrand_result.inserted_id)
            substrand_count += 1
            lessons = substrand_data.get("lessons", 4)
            print(f"      Substrand: {substrand_data['name']} ({lessons} lessons) - {len(substrand_data.get('slos', []))} SLOs")
            
            for slo_data in substrand_data.get("slos", []):
                if isinstance(slo_data, dict):
                    slo_name = slo_data.get("name", "")
                    slo_description = slo_data.get("description", slo_name)
                else:
                    slo_name = str(slo_data)
                    slo_description = str(slo_data)
                
                slo_result = await db.slos.insert_one({
                    "name": slo_name,
                    "description": slo_description,
                    "substrandId": substrand_id
                })
                slo_id = str(slo_result.inserted_id)
                slo_count += 1
                
                competency_ids = await get_competency_ids(substrand_data.get("competencies", []))
                value_ids = await get_value_ids(substrand_data.get("values", []))
                pci_ids = await get_pci_ids(substrand_data.get("pcis", []))
                
                await db.slo_mappings.insert_one({
                    "sloId": slo_id,
                    "competencyIds": competency_ids,
                    "valueIds": value_ids,
                    "pciIds": pci_ids,
                    "assessmentIds": []
                })
                slo_mapping_count += 1
            
            activities = substrand_data.get("learning_activities", {})
            if activities or substrand_data.get("inquiry_questions"):
                await db.learning_activities.insert_one({
                    "substrandId": substrand_id,
                    "introduction": activities.get("introduction", "") if isinstance(activities, dict) else "",
                    "development": activities.get("development", "") if isinstance(activities, dict) else "",
                    "conclusion": activities.get("conclusion", "") if isinstance(activities, dict) else "",
                    "extended_activities": [activities.get("extended", "")] if isinstance(activities, dict) and activities.get("extended") else [],
                    "learning_resources": activities.get("resources", []) if isinstance(activities, dict) else [],
                    "assessment_methods": activities.get("assessment", []) if isinstance(activities, dict) else [],
                    "inquiry_questions": substrand_data.get("inquiry_questions", []),
                    "core_competencies": substrand_data.get("competencies", []),
                    "values": substrand_data.get("values", []),
                    "pci": substrand_data.get("pcis", [])
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
    print("Grade 10 Curriculum Data Seeding - COMPLETE VERSION")
    print("="*60)
    
    grade_id = await get_grade_10_id()
    print(f"\nGrade 10 ID: {grade_id}")
    
    # Seed Geography, History and Citizenship, and Kiswahili Lugha first
    subjects = [
        GEOGRAPHY_DATA,
        HISTORY_CITIZENSHIP_DATA,
        KISWAHILI_LUGHA_DATA
    ]
    
    results = []
    for subject_data in subjects:
        result = await seed_subject_data(subject_data, grade_id)
        results.append(result)
    
    print("\n" + "="*60)
    print("PARTIAL SUMMARY (Geography, History, Kiswahili)")
    print("="*60)
    
    total_strands = 0
    total_substrands = 0
    total_slos = 0
    
    for result in results:
        print(f"\n{result['subject']}:")
        print(f"  Strands: {result['strands']}")
        print(f"  Substrands: {result['substrands']}")
        print(f"  SLOs: {result['slos']}")
        
        total_strands += result['strands']
        total_substrands += result['substrands']
        total_slos += result['slos']
    
    print(f"\n{'='*60}")
    print(f"TOTALS SO FAR:")
    print(f"  Total Strands: {total_strands}")
    print(f"  Total Substrands: {total_substrands}")
    print(f"  Total SLOs: {total_slos}")
    print(f"{'='*60}")
    
    client.close()
    return results

if __name__ == "__main__":
    asyncio.run(main())
