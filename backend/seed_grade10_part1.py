"""
Grade 10 Curriculum Seeding Script
Seeds: Agriculture, Computer Science, Fasihi ya Kiswahili, History and Citizenship, Home Science
Data extracted exactly from KICD Kenya curriculum PDFs
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv(Path(__file__).parent / '.env')

mongo_url = os.environ.get('MONGO_URL') or os.environ.get('MONGODB_URI')
if not mongo_url:
    raise ValueError("MONGO_URL or MONGODB_URI environment variable is required")

client = AsyncIOMotorClient(mongo_url)
db = client['cbeplanner']

# Standard competencies, values, PCIs for reference
COMPETENCIES = [
    "Communication and Collaboration",
    "Critical Thinking and Problem Solving",
    "Creativity and Imagination",
    "Citizenship",
    "Digital Literacy",
    "Learning to Learn",
    "Self-Efficacy"
]

VALUES = [
    "Unity",
    "Love",
    "Peace",
    "Respect",
    "Responsibility",
    "Integrity",
    "Patriotism",
    "Social Justice"
]

PCIS = [
    "Life Skills",
    "Health Education",
    "Environmental Education",
    "Citizenship Education",
    "Financial Literacy",
    "Safety and Security",
    "Social Cohesion"
]

# ============================================================================
# AGRICULTURE DATA (Grade 10)
# Extracted from Agriculture.pdf
# ============================================================================
AGRICULTURE_DATA = {
    "name": "Agriculture",
    "strands": [
        {
            "name": "Crop Production",
            "substrands": [
                {
                    "name": "Agricultural Land",
                    "slos": [
                        {
                            "name": "Ways of accessing land for agricultural use",
                            "description": "By the end of the sub strand the learner should be able to describe ways of accessing land for agricultural use including leasing, inheriting, buying and donation",
                            "learning_experiences": [
                                "Discuss with resource person ways of accessing land for agricultural use including leasing, inheriting, buying and donation",
                                "Take an excursion in the community to study and assess different forms of land and discuss the possible utilities of the land",
                                "Use digital devices to search for information on natural factors that determine productivity of land such as climate, altitude, soil factors, topography and biotic factors",
                                "Make class presentations on importance of land in agricultural production"
                            ],
                            "inquiry_questions": ["How is land productivity determined for agriculture?", "Why is land put into different agricultural uses?"],
                            "competencies": ["Citizenship", "Communication and Collaboration"],
                            "pcis": ["Social Economic and Environmental Issues", "Biodiversity"],
                            "values": ["Respect", "Social Justice"]
                        },
                        {
                            "name": "Evaluate utility of land for agricultural production",
                            "description": "By the end of the sub strand the learner should be able to evaluate utility of land for agricultural production purposes",
                            "learning_experiences": ["Take an excursion in the community to study and assess different forms of land and discuss the possible utilities"],
                            "inquiry_questions": ["Why is land put into different agricultural uses?"],
                            "competencies": ["Critical Thinking and Problem Solving"],
                            "pcis": ["Environmental Education"],
                            "values": ["Responsibility"]
                        },
                        {
                            "name": "Natural factors that determine productivity of land",
                            "description": "By the end of the sub strand the learner should be able to analyse natural factors that determine productivity of land in agriculture including climate, altitude, soil factors, topography and biotic factors",
                            "learning_experiences": ["Use digital devices to search for information on natural factors that determine productivity of land"],
                            "inquiry_questions": ["How is land productivity determined for agriculture?"],
                            "competencies": ["Digital Literacy"],
                            "pcis": ["Environmental Education"],
                            "values": ["Responsibility"]
                        }
                    ]
                },
                {
                    "name": "Properties of Soil",
                    "slos": [
                        {
                            "name": "Physical, chemical and biological properties of soil",
                            "description": "By the end of the sub strand the learner should be able to describe properties of a soil for crop production including physical, chemical and biological properties",
                            "learning_experiences": [
                                "Discuss on physical, chemical and biological properties of soil for crop production",
                                "Conduct experiments to test physical properties (porosity, texture) chemical properties (soil pH) and biological properties (humus)",
                                "Take field excursion, observe and relate soil profile to crop farming activities",
                                "Use digital and non-digital resources to search for importance of soil properties in crop production"
                            ],
                            "inquiry_questions": ["How do properties of soil influence crop production?"],
                            "competencies": ["Digital Literacy", "Self-Efficacy", "Creativity and Imagination"],
                            "pcis": ["Social Economic and Environmental Issues", "Life Skills"],
                            "values": ["Unity", "Respect"]
                        },
                        {
                            "name": "Investigate properties of soil for crop production",
                            "description": "By the end of the sub strand the learner should be able to investigate the properties of soil for crop production through experiments",
                            "learning_experiences": ["Conduct experiments to test physical properties (porosity, texture) chemical properties (soil pH) and biological properties (humus)"],
                            "inquiry_questions": ["How do properties of soil influence crop production?"],
                            "competencies": ["Creativity and Imagination"],
                            "pcis": ["Life Skills"],
                            "values": ["Unity"]
                        },
                        {
                            "name": "Soil profile and crop production",
                            "description": "By the end of the sub strand the learner should be able to relate importance of soil profile to crop production",
                            "learning_experiences": ["Take field excursion, observe and relate soil profile to crop farming activities"],
                            "inquiry_questions": ["How do properties of soil influence crop production?"],
                            "competencies": ["Critical Thinking and Problem Solving"],
                            "pcis": ["Environmental Education"],
                            "values": ["Responsibility"]
                        }
                    ]
                },
                {
                    "name": "Land Preparation",
                    "slos": [
                        {
                            "name": "Activities of fallow land preparation",
                            "description": "By the end of the sub strand the learner should be able to describe activities of fallow land preparation to appropriate seedbed including land clearing, primary cultivation, secondary cultivation, tertiary operations",
                            "learning_experiences": [
                                "Brainstorm on the activities carried out on fallow land to prepare appropriate seedbed (land clearing, primary cultivation, secondary cultivation, tertiary operations)",
                                "Carry out applicable activities on fallow land to prepare it for establishment of a selected crop",
                                "Assess status of land for production of selected crop and apply applicable conservation tillage practices such as zero tillage and minimum tillage",
                                "Make presentations on importance of proper land preparations in crop production"
                            ],
                            "inquiry_questions": ["How does proper land preparation contribute to crop production?"],
                            "competencies": ["Critical Thinking and Problem Solving", "Citizenship"],
                            "pcis": ["Life Skills", "Safety and Security"],
                            "values": ["Peace", "Unity"]
                        },
                        {
                            "name": "Carry out land preparation operations",
                            "description": "By the end of the sub strand the learner should be able to carry out land preparation operations for selected crop",
                            "learning_experiences": ["Carry out applicable activities on fallow land to prepare it for establishment of a selected crop"],
                            "inquiry_questions": ["How does proper land preparation contribute to crop production?"],
                            "competencies": ["Self-Efficacy"],
                            "pcis": ["Life Skills"],
                            "values": ["Responsibility"]
                        },
                        {
                            "name": "Conservation tillage in crop production",
                            "description": "By the end of the sub strand the learner should be able to apply conservation tillage in crop production including zero tillage and minimum tillage",
                            "learning_experiences": ["Assess status of land for production of selected crop and apply applicable conservation tillage practices"],
                            "inquiry_questions": ["How does proper land preparation contribute to crop production?"],
                            "competencies": ["Critical Thinking and Problem Solving"],
                            "pcis": ["Environmental Education"],
                            "values": ["Responsibility"]
                        }
                    ]
                },
                {
                    "name": "Field Management Practices",
                    "slos": [
                        {
                            "name": "Management practices of vegetable and perennial crops",
                            "description": "By the end of the sub strand the learner should be able to describe management practices of selected vegetable and perennial crops including pruning and top dressing",
                            "learning_experiences": [
                                "Use digital devices to search for information or take a field trip to study pruning of vegetables such as capsicum and tomatoes; and perennial crops that require cutting back, single stem and multiple stem pruning",
                                "Carry out pruning of selected vegetable crops such as tomatoes and capsicum",
                                "Discuss and carry out top dressing of selected crops using appropriate fertilizers and top-dressing methods",
                                "Make a field trip to study and appreciate importance of selected field management practices in crop production"
                            ],
                            "inquiry_questions": ["How do field management practices influence crop production?"],
                            "competencies": ["Communication and Collaboration", "Self-Efficacy"],
                            "pcis": ["Financial Literacy", "Environmental Education"],
                            "values": ["Respect", "Responsibility"]
                        },
                        {
                            "name": "Carry out field management practices",
                            "description": "By the end of the sub strand the learner should be able to carry out selected management practices in crop production",
                            "learning_experiences": ["Carry out pruning of selected vegetable crops", "Carry out top dressing of selected crops"],
                            "inquiry_questions": ["How do field management practices influence crop production?"],
                            "competencies": ["Self-Efficacy"],
                            "pcis": ["Life Skills"],
                            "values": ["Responsibility"]
                        }
                    ]
                },
                {
                    "name": "Growing Selected Crops",
                    "slos": [
                        {
                            "name": "Crops established through the nursery",
                            "description": "By the end of the sub strand the learner should be able to determine crops that are established through the nursery",
                            "learning_experiences": [
                                "Brainstorm to determine appropriate crop such as vegetables or any other crop that is established from the nursery",
                                "Establish and carry out appropriate management practices for a selected crop during the growth cycle",
                                "Make class presentations on field management practices adopted and carried out on the selected crop"
                            ],
                            "inquiry_questions": ["How do management practices influence crop productivity?"],
                            "competencies": ["Creativity and Imagination", "Self-Efficacy"],
                            "pcis": ["Learner Support Programme", "Safety and Security"],
                            "values": ["Responsibility", "Respect"]
                        },
                        {
                            "name": "Grow a selected crop with appropriate management",
                            "description": "By the end of the sub strand the learner should be able to grow a selected crop applying appropriate management practices",
                            "learning_experiences": ["Establish and carry out appropriate management practices for a selected crop during the growth cycle"],
                            "inquiry_questions": ["How do management practices influence crop productivity?"],
                            "competencies": ["Self-Efficacy"],
                            "pcis": ["Life Skills"],
                            "values": ["Responsibility"]
                        }
                    ]
                },
                {
                    "name": "Crop Protection",
                    "slos": [
                        {
                            "name": "Identify and classify weeds",
                            "description": "By the end of the sub strand the learner should be able to identify weeds in a crop field and classify weeds based on morphology and life cycle",
                            "learning_experiences": [
                                "Take excursion to identify weeds in a crop field and make herbarium",
                                "Use digital and non-digital resources to classify weeds based on morphology, and life cycle",
                                "Discuss in groups the methods of weed control (physical; cultural; biological; chemical; legislative methods)",
                                "Carry out weed control in a crop field using appropriate method",
                                "Discuss and make class presentations on pros and cons on weeds to a farming household"
                            ],
                            "inquiry_questions": ["How do weeds affect crop production?", "Why is weed control done in crop production?"],
                            "competencies": ["Digital Literacy", "Learning to Learn"],
                            "pcis": ["Financial Literacy", "Learner Support Programme"],
                            "values": ["Responsibility", "Respect"]
                        },
                        {
                            "name": "Methods of weed control",
                            "description": "By the end of the sub strand the learner should be able to describe methods of weed control including physical, cultural, biological, chemical, and legislative methods",
                            "learning_experiences": ["Discuss in groups the methods of weed control"],
                            "inquiry_questions": ["Why is weed control done in crop production?"],
                            "competencies": ["Communication and Collaboration"],
                            "pcis": ["Life Skills"],
                            "values": ["Unity"]
                        },
                        {
                            "name": "Carry out weed control",
                            "description": "By the end of the sub strand the learner should be able to carry out weed control using appropriate methods",
                            "learning_experiences": ["Carry out weed control in a crop field using appropriate method"],
                            "inquiry_questions": ["Why is weed control done in crop production?"],
                            "competencies": ["Self-Efficacy"],
                            "pcis": ["Life Skills"],
                            "values": ["Responsibility"]
                        }
                    ]
                },
                {
                    "name": "General Crop Harvesting",
                    "slos": [
                        {
                            "name": "Factors that determine harvesting",
                            "description": "By the end of the sub strand the learner should be able to explain factors that determine harvesting of a crop produce including timing, stage of growth, and purpose",
                            "learning_experiences": [
                                "Discuss and search on digital devices for factors that determine harvesting of crop produce (timing, stage of growth, purpose)",
                                "Carry out harvesting process (pre-harvest practices, harvesting and post-harvest practices) for tubers and cereals",
                                "Discuss with a resource person on the importance of harvesting process in crop production"
                            ],
                            "inquiry_questions": ["How does harvesting process affect the quantity and quality of crop produce?"],
                            "competencies": ["Citizenship", "Critical Thinking and Problem Solving"],
                            "pcis": ["Life Skills", "Learner Support Programme"],
                            "values": ["Integrity", "Unity"]
                        },
                        {
                            "name": "Carry out harvesting process",
                            "description": "By the end of the sub strand the learner should be able to carry out the harvesting process for selected crop produce including pre-harvest, harvesting and post-harvest practices",
                            "learning_experiences": ["Carry out harvesting process for tubers and cereals"],
                            "inquiry_questions": ["How does harvesting process affect the quantity and quality of crop produce?"],
                            "competencies": ["Self-Efficacy"],
                            "pcis": ["Life Skills"],
                            "values": ["Responsibility"]
                        }
                    ]
                }
            ]
        },
        {
            "name": "Animal Production",
            "substrands": [
                {
                    "name": "Breeds of Livestock",
                    "slos": [
                        {
                            "name": "Breeds of livestock based on uses",
                            "description": "By the end of the sub strand the learner should be able to describe breeds of livestock (cattle, pigs, rabbits, sheep, goats) based on their uses",
                            "learning_experiences": [
                                "Use information from digital and print resources to describe breeds of cattle, pigs, rabbits, sheep and goats",
                                "Take a field trip, excursion or observe resource media to distinguish common breed livestock based on their observable characteristics",
                                "Discuss and make presentations on comparative productivity from various livestock breeds"
                            ],
                            "inquiry_questions": ["How does livestock breeds affect productivity of animals?"],
                            "competencies": ["Digital Literacy", "Communication and Collaboration"],
                            "pcis": ["Financial Literacy", "Safety and Security"],
                            "values": ["Unity", "Respect"]
                        },
                        {
                            "name": "Distinguish livestock breeds by characteristics",
                            "description": "By the end of the sub strand the learner should be able to distinguish common breed livestock based on their characteristics",
                            "learning_experiences": ["Take a field trip or observe resource media to distinguish common breed livestock"],
                            "inquiry_questions": ["How does livestock breeds affect productivity of animals?"],
                            "competencies": ["Critical Thinking and Problem Solving"],
                            "pcis": ["Life Skills"],
                            "values": ["Respect"]
                        }
                    ]
                },
                {
                    "name": "Animal Handling and Safety",
                    "slos": [
                        {
                            "name": "Forms of animal handling",
                            "description": "By the end of the sub strand the learner should be able to examine forms of animal handling in the community and describe inhumane treatments",
                            "learning_experiences": [
                                "Discuss inhumane treatments such as beating, poor restraining, inappropriate castration, poor transport methods, inappropriate harnessing, inhumane slaughtering, overloading draught animals, and over working",
                                "Use digital devices to observe and describe structures used to ensure safe handling of domestic animals",
                                "Discuss ways of ensuring safety of persons handling domestic animals through methods such as restraining animals, correct position when handling, holding appropriate parts and ensuring safe distance",
                                "Use tools and equipment used to ensure safety in handling domestic animals; tools to include halter, restraining rope, bull ring and lead stick",
                                "Take an excursion to nearby farms to observe animal handling and present suggestions on how animal safety could be enhanced in the community"
                            ],
                            "inquiry_questions": ["How can we ensure safety when handling animals?"],
                            "competencies": ["Citizenship"],
                            "pcis": ["Safety of Animals and Animal Handlers"],
                            "values": ["Love"]
                        },
                        {
                            "name": "Structures for safe handling of animals",
                            "description": "By the end of the sub strand the learner should be able to describe the structures used to ensure safety in handling domestic animals",
                            "learning_experiences": ["Use digital devices to observe and describe structures used to ensure safe handling"],
                            "inquiry_questions": ["How can we ensure safety when handling animals?"],
                            "competencies": ["Digital Literacy"],
                            "pcis": ["Safety and Security"],
                            "values": ["Responsibility"]
                        },
                        {
                            "name": "Tools and equipment for animal safety",
                            "description": "By the end of the sub strand the learner should be able to use tools and equipment to ensure safety in handling domestic animals including halter, restraining rope, bull ring and lead stick",
                            "learning_experiences": ["Use tools and equipment to ensure safety in handling domestic animals"],
                            "inquiry_questions": ["How can we ensure safety when handling animals?"],
                            "competencies": ["Self-Efficacy"],
                            "pcis": ["Safety and Security"],
                            "values": ["Responsibility"]
                        }
                    ]
                },
                {
                    "name": "General Animal Health",
                    "slos": [
                        {
                            "name": "Benefits of keeping animals healthy",
                            "description": "By the end of the sub strand the learner should be able to explain the benefits of keeping animals healthy in livestock production",
                            "learning_experiences": [
                                "Use information from digital and print resources to explain the benefits of keeping animals healthy in livestock production",
                                "Discuss with resource person and observe animals in a herd to identify signs of ill health",
                                "Discuss and suggest general preventative and control measures of ill health in livestock production",
                                "Practise applicable measures that maintain animal health in livestock production and apply them in rearing available animals in school"
                            ],
                            "inquiry_questions": ["How is animal health important in animal production?"],
                            "competencies": ["Citizenship", "Creativity and Imagination"],
                            "pcis": ["Life Skills", "Animal Welfare"],
                            "values": ["Patriotism", "Integrity"]
                        },
                        {
                            "name": "Signs of ill health in livestock",
                            "description": "By the end of the sub strand the learner should be able to identify signs of ill health in livestock production",
                            "learning_experiences": ["Discuss with resource person and observe animals in a herd to identify signs of ill health"],
                            "inquiry_questions": ["How is animal health important in animal production?"],
                            "competencies": ["Critical Thinking and Problem Solving"],
                            "pcis": ["Health Education"],
                            "values": ["Responsibility"]
                        },
                        {
                            "name": "Control measures of ill health",
                            "description": "By the end of the sub strand the learner should be able to propose general control measures of ill health in livestock production",
                            "learning_experiences": ["Discuss and suggest general preventative and control measures of ill health"],
                            "inquiry_questions": ["How is animal health important in animal production?"],
                            "competencies": ["Critical Thinking and Problem Solving"],
                            "pcis": ["Health Education"],
                            "values": ["Responsibility"]
                        }
                    ]
                },
                {
                    "name": "Bee Keeping",
                    "slos": [
                        {
                            "name": "Factors in siting an apiary",
                            "description": "By the end of the sub strand the learner should be able to explain the factors to consider in siting an apiary",
                            "learning_experiences": [
                                "Discuss the factors to consider in siting an apiary",
                                "Use digital devices or print resources to acquire information on how to stock a hive, then describe the process in class plenary",
                                "Deliberate with a resource person and participate in a guided process of carrying out safe apiary management practices",
                                "Use an empty hive or model of a hive to role play the honey harvesting process"
                            ],
                            "inquiry_questions": ["How are bees reared?"],
                            "competencies": ["Digital Literacy", "Self-Efficacy"],
                            "pcis": ["Health Promotion Issues", "Safety and Security"],
                            "values": ["Responsibility", "Unity"]
                        },
                        {
                            "name": "Process of stocking a hive",
                            "description": "By the end of the sub strand the learner should be able to describe the process of stocking a hive",
                            "learning_experiences": ["Use digital devices or print resources to acquire information on how to stock a hive"],
                            "inquiry_questions": ["How are bees reared?"],
                            "competencies": ["Digital Literacy"],
                            "pcis": ["Life Skills"],
                            "values": ["Responsibility"]
                        },
                        {
                            "name": "Safe apiary management practices",
                            "description": "By the end of the sub strand the learner should be able to carry out safe apiary management practices",
                            "learning_experiences": ["Deliberate with a resource person and participate in a guided process of carrying out safe apiary management practices"],
                            "inquiry_questions": ["How are bees reared?"],
                            "competencies": ["Self-Efficacy"],
                            "pcis": ["Safety and Security"],
                            "values": ["Responsibility"]
                        },
                        {
                            "name": "Honey harvesting process",
                            "description": "By the end of the sub strand the learner should be able to demonstrate honey harvesting process",
                            "learning_experiences": ["Use an empty hive or model of a hive to role play the honey harvesting process"],
                            "inquiry_questions": ["How are bees reared?"],
                            "competencies": ["Self-Efficacy"],
                            "pcis": ["Life Skills"],
                            "values": ["Unity"]
                        }
                    ]
                },
                {
                    "name": "Animal Rearing Project",
                    "slos": [
                        {
                            "name": "Project plan on rearing a selected animal",
                            "description": "By the end of the sub strand the learner should be able to develop a project plan on rearing a selected animal",
                            "learning_experiences": [
                                "Adopt a project template to write a project plan on rearing a selected animal (mammals, birds, insects)",
                                "Brainstorm on appropriate animal rearing project, develop project details and simple budget",
                                "Select the site for the project, install the required animal structures, prepare appropriate record templates and routine duty schedule",
                                "Stock and manage the animal project as per the project plan",
                                "Make class presentations on the success and areas of improvements to evaluate the animal rearing practices carried out in the project"
                            ],
                            "inquiry_questions": ["How can animal rearing project be carried out?"],
                            "competencies": ["Critical Thinking and Problem Solving", "Creativity and Imagination"],
                            "pcis": ["Learner Support Programme", "Social Cohesion", "Financial Literacy"],
                            "values": ["Love", "Social Justice"]
                        },
                        {
                            "name": "Budget for animal rearing project",
                            "description": "By the end of the sub strand the learner should be able to prepare a budget for the animal rearing project",
                            "learning_experiences": ["Brainstorm on appropriate animal rearing project, develop project details and simple budget"],
                            "inquiry_questions": ["How can animal rearing project be carried out?"],
                            "competencies": ["Critical Thinking and Problem Solving"],
                            "pcis": ["Financial Literacy"],
                            "values": ["Responsibility"]
                        },
                        {
                            "name": "Implement the animal rearing project plan",
                            "description": "By the end of the sub strand the learner should be able to implement the plan for the animal rearing project",
                            "learning_experiences": ["Select the site for the project, install the required animal structures, prepare appropriate record templates"],
                            "inquiry_questions": ["How can animal rearing project be carried out?"],
                            "competencies": ["Self-Efficacy"],
                            "pcis": ["Life Skills"],
                            "values": ["Responsibility"]
                        },
                        {
                            "name": "Routine management practices",
                            "description": "By the end of the sub strand the learner should be able to carry out routine management practices on the animal rearing project",
                            "learning_experiences": ["Stock and manage the animal project as per the project plan"],
                            "inquiry_questions": ["How can animal rearing project be carried out?"],
                            "competencies": ["Self-Efficacy"],
                            "pcis": ["Life Skills"],
                            "values": ["Responsibility"]
                        },
                        {
                            "name": "Evaluate animal rearing practices",
                            "description": "By the end of the sub strand the learner should be able to evaluate the animal rearing practices carried out in the project",
                            "learning_experiences": ["Make class presentations on the success and areas of improvements"],
                            "inquiry_questions": ["How can animal rearing project be carried out?"],
                            "competencies": ["Critical Thinking and Problem Solving"],
                            "pcis": ["Life Skills"],
                            "values": ["Integrity"]
                        }
                    ]
                }
            ]
        },
        {
            "name": "Agricultural Technologies and Entrepreneurship",
            "substrands": [
                {
                    "name": "Tools and Equipment",
                    "slos": [
                        {
                            "name": "Tools and equipment for agricultural tasks",
                            "description": "By the end of the sub strand the learner should be able to identify tools and equipment used for various agricultural tasks including gardening, livestock production, assembling and dissembling tasks",
                            "learning_experiences": [
                                "Observe and analyse tools and equipment used for various agricultural tasks (gardening tasks; livestock production tasks; assembling and dissembling tasks)",
                                "Conduct various agricultural tasks using appropriate tools and equipment",
                                "Carry out maintenance practices (cleaning, sharpening, lubrication, part repairs and replacements, parts tightening, painting) on selected tools and equipment",
                                "Practise the care and safety in use of tools and equipment such as appropriate storage, correct usage, safe distance, appropriate personal protective equipment",
                                "Discuss and make presentations on importance of maintaining tools and equipment used in agricultural tasks"
                            ],
                            "inquiry_questions": ["How do tools and equipment contribute to efficiency of farm operations?"],
                            "competencies": ["Self-Efficacy", "Creativity and Imagination"],
                            "pcis": ["Health Promotion Issues", "Safety and Security"],
                            "values": ["Responsibility", "Respect"]
                        },
                        {
                            "name": "Maintenance practices on tools and equipment",
                            "description": "By the end of the sub strand the learner should be able to carry out appropriate maintenance practices on selected tools and equipment",
                            "learning_experiences": ["Carry out maintenance practices on selected tools and equipment"],
                            "inquiry_questions": ["How do tools and equipment contribute to efficiency of farm operations?"],
                            "competencies": ["Self-Efficacy"],
                            "pcis": ["Life Skills"],
                            "values": ["Responsibility"]
                        },
                        {
                            "name": "Safety measures in use of tools",
                            "description": "By the end of the sub strand the learner should be able to apply safety measures in the use of tools and equipment",
                            "learning_experiences": ["Practise the care and safety in use of tools and equipment"],
                            "inquiry_questions": ["How do tools and equipment contribute to efficiency of farm operations?"],
                            "competencies": ["Self-Efficacy"],
                            "pcis": ["Safety and Security"],
                            "values": ["Responsibility"]
                        }
                    ]
                },
                {
                    "name": "Product Processing and Value Addition",
                    "slos": [
                        {
                            "name": "Methods of value addition",
                            "description": "By the end of the sub strand the learner should be able to suggest methods of value addition for selected agricultural produce",
                            "learning_experiences": [
                                "Use digital and non-digital resources to search for information and suggest methods applicable for value addition of selected agricultural produce",
                                "Discuss with resource person on use of applicable methods/techniques to carry out processing of agricultural produce of plant origin such as vegetables, nuts, fruits, cereals, tubers and pulses into Jam, butter, marmalade, ketchup, juices, flour, puree/concentrate of semi-solid fruit extracts, crisps among others",
                                "Discuss with resource person applicable methods/techniques to carry out processing of produce of animal origin such as honey, milk, hides and skins, meat or fish",
                                "Visit market outlets to observe and study applicable methods to carry out home-based packaging and branding of processed agricultural products",
                                "Discuss and present ethical concerns in processing and value addition of various agricultural produce"
                            ],
                            "inquiry_questions": ["How does value addition enhance nutrition and food security?"],
                            "competencies": ["Self-Efficacy", "Critical Thinking and Problem Solving"],
                            "pcis": ["Life Skills", "Health Promotion Issues", "Financial Literacy"],
                            "values": ["Responsibility", "Peace"]
                        },
                        {
                            "name": "Processing produce of plant origin",
                            "description": "By the end of the sub strand the learner should be able to carry out processing of agricultural produce of plant origin",
                            "learning_experiences": ["Discuss with resource person on use of applicable methods/techniques to carry out processing of agricultural produce of plant origin"],
                            "inquiry_questions": ["How does value addition enhance nutrition and food security?"],
                            "competencies": ["Self-Efficacy"],
                            "pcis": ["Health Education"],
                            "values": ["Responsibility"]
                        },
                        {
                            "name": "Processing produce of animal origin",
                            "description": "By the end of the sub strand the learner should be able to carry out processing of agricultural produce of animal origin",
                            "learning_experiences": ["Discuss with resource person applicable methods/techniques to carry out processing of produce of animal origin"],
                            "inquiry_questions": ["How does value addition enhance nutrition and food security?"],
                            "competencies": ["Self-Efficacy"],
                            "pcis": ["Health Education"],
                            "values": ["Responsibility"]
                        },
                        {
                            "name": "Home-based packaging and branding",
                            "description": "By the end of the sub strand the learner should be able to carry out home-based packaging and branding of processed agricultural products",
                            "learning_experiences": ["Visit market outlets to observe and study applicable methods to carry out home-based packaging and branding"],
                            "inquiry_questions": ["How does value addition enhance nutrition and food security?"],
                            "competencies": ["Creativity and Imagination"],
                            "pcis": ["Financial Literacy"],
                            "values": ["Integrity"]
                        },
                        {
                            "name": "Ethical issues in processing",
                            "description": "By the end of the sub strand the learner should be able to appraise ethical issues in the processing and value addition processes",
                            "learning_experiences": ["Discuss and present ethical concerns in processing and value addition"],
                            "inquiry_questions": ["How does value addition enhance nutrition and food security?"],
                            "competencies": ["Critical Thinking and Problem Solving"],
                            "pcis": ["Citizenship Education"],
                            "values": ["Integrity"]
                        }
                    ]
                },
                {
                    "name": "Establishing Agricultural Enterprise",
                    "slos": [
                        {
                            "name": "Factors of production in agricultural enterprise",
                            "description": "By the end of the sub strand the learner should be able to explain factors of production in an agricultural enterprise including land/space, labour, entrepreneurship, capital",
                            "learning_experiences": [
                                "Discuss the factors of production in an agricultural enterprise (land/space, labour, entrepreneurship, capital)",
                                "Discuss with a resource person to suggest ways of mobilizing capital to establish an agricultural enterprise such as borrowing, savings, disposing-off assets, grants and donations",
                                "Use digital and non-digital resources to search and examine factors to consider in selecting an agricultural enterprise",
                                "Discuss with a resource person to evaluate appropriate sources of support services for agricultural enterprise",
                                "Discuss and present the role of various factors of production in establishing an agricultural enterprise"
                            ],
                            "inquiry_questions": ["How do we establish an agricultural enterprise?"],
                            "competencies": ["Critical Thinking and Problem Solving", "Creativity and Imagination"],
                            "pcis": ["Financial Literacy", "Learner Support Programme"],
                            "values": ["Patriotism", "Respect"]
                        },
                        {
                            "name": "Ways of acquiring capital",
                            "description": "By the end of the sub strand the learner should be able to propose ways of acquiring capital to establish an agricultural enterprise",
                            "learning_experiences": ["Discuss with a resource person to suggest ways of mobilizing capital"],
                            "inquiry_questions": ["How do we establish an agricultural enterprise?"],
                            "competencies": ["Critical Thinking and Problem Solving"],
                            "pcis": ["Financial Literacy"],
                            "values": ["Responsibility"]
                        },
                        {
                            "name": "Factors in selecting agricultural enterprise",
                            "description": "By the end of the sub strand the learner should be able to examine factors to consider in selecting an agricultural enterprise",
                            "learning_experiences": ["Use digital and non-digital resources to search and examine factors to consider in selecting an agricultural enterprise"],
                            "inquiry_questions": ["How do we establish an agricultural enterprise?"],
                            "competencies": ["Digital Literacy"],
                            "pcis": ["Life Skills"],
                            "values": ["Responsibility"]
                        },
                        {
                            "name": "Sources of support services",
                            "description": "By the end of the sub strand the learner should be able to evaluate sources of support services for agricultural enterprise",
                            "learning_experiences": ["Discuss with a resource person to evaluate appropriate sources of support services"],
                            "inquiry_questions": ["How do we establish an agricultural enterprise?"],
                            "competencies": ["Critical Thinking and Problem Solving"],
                            "pcis": ["Life Skills"],
                            "values": ["Respect"]
                        }
                    ]
                },
                {
                    "name": "Marketing Agricultural Produce",
                    "slos": [
                        {
                            "name": "Preparing produce for marketing",
                            "description": "By the end of the sub strand the learner should be able to describe ways of preparing agricultural produce for marketing including weighing, sorting, grading, packaging, branding and labeling",
                            "learning_experiences": [
                                "Discuss ways of preparing agricultural produce for marketing such as weighing, sorting, grading, packaging, branding and labeling",
                                "Visit an agricultural market outlet to observe and learn how different agricultural produce are weighed, sorted, graded, packaged, branded, labelled and displayed",
                                "Demonstrate how to prepare samples of selected agricultural produce for marketing",
                                "Discuss various market outlets for agricultural produce (digital platforms and physical market outlets)",
                                "Inquire from a resource person expenses incurred in marketing activities such as transportation costs, advertisement costs, market authority charges and taxes",
                                "Share experiences on benefits of preparing agricultural produce for marketing"
                            ],
                            "inquiry_questions": ["How can we prepare agricultural produce for the market?"],
                            "competencies": ["Self-Efficacy"],
                            "pcis": ["Financial Literacy"],
                            "values": ["Integrity"]
                        },
                        {
                            "name": "Market outlets for agricultural produce",
                            "description": "By the end of the sub strand the learner should be able to discuss market outlets for agricultural produce including digital platforms and physical market outlets",
                            "learning_experiences": ["Discuss various market outlets for agricultural produce"],
                            "inquiry_questions": ["How can we prepare agricultural produce for the market?"],
                            "competencies": ["Digital Literacy"],
                            "pcis": ["Financial Literacy"],
                            "values": ["Responsibility"]
                        },
                        {
                            "name": "Expenses in marketing agricultural produce",
                            "description": "By the end of the sub strand the learner should be able to evaluate expenses incurred in marketing agricultural produce",
                            "learning_experiences": ["Inquire from a resource person expenses incurred in marketing activities"],
                            "inquiry_questions": ["How can we prepare agricultural produce for the market?"],
                            "competencies": ["Critical Thinking and Problem Solving"],
                            "pcis": ["Financial Literacy"],
                            "values": ["Responsibility"]
                        }
                    ]
                },
                {
                    "name": "Composting Techniques",
                    "slos": [
                        {
                            "name": "Composting in organic manure production",
                            "description": "By the end of the sub strand the learner should be able to describe composting in production of organic manure including conventional and innovative methods",
                            "learning_experiences": [
                                "Use ideas from digital and non-digital resources to describe methods of composting (conventional methods; innovative methods) and appropriate materials for composting at farm level",
                                "Discuss and present factors that influence quality of compost manure (materials, process of composting, storage)",
                                "Follow procedure provided by resource person or other sources to carry out composting for production of organic manure through pit and heap methods",
                                "Use digital resources to acquire ideas and carry out innovative composting such as vermi-composting and containerized composting for production of organic manure",
                                "Utilize the compost manure to existing crop enterprises to appreciate role of composting in soil improvement"
                            ],
                            "inquiry_questions": ["Why is composting relevant in soil improvement?"],
                            "competencies": ["Digital Literacy", "Creativity and Imagination"],
                            "pcis": ["Learner Support Programme", "Biodiversity Conservation"],
                            "values": ["Responsibility", "Respect"]
                        },
                        {
                            "name": "Factors affecting quality of compost",
                            "description": "By the end of the sub strand the learner should be able to examine factors that influence quality of compost manure",
                            "learning_experiences": ["Discuss and present factors that influence quality of compost manure"],
                            "inquiry_questions": ["Why is composting relevant in soil improvement?"],
                            "competencies": ["Critical Thinking and Problem Solving"],
                            "pcis": ["Environmental Education"],
                            "values": ["Responsibility"]
                        },
                        {
                            "name": "Conventional composting methods",
                            "description": "By the end of the sub strand the learner should be able to carry out conventional composting methods for production of organic manure through pit and heap methods",
                            "learning_experiences": ["Follow procedure provided by resource person to carry out composting through pit and heap methods"],
                            "inquiry_questions": ["Why is composting relevant in soil improvement?"],
                            "competencies": ["Self-Efficacy"],
                            "pcis": ["Environmental Education"],
                            "values": ["Responsibility"]
                        },
                        {
                            "name": "Innovative composting methods",
                            "description": "By the end of the sub strand the learner should be able to carry out innovative composting methods including vermi-composting and containerized composting",
                            "learning_experiences": ["Use digital resources to acquire ideas and carry out innovative composting"],
                            "inquiry_questions": ["Why is composting relevant in soil improvement?"],
                            "competencies": ["Creativity and Imagination", "Digital Literacy"],
                            "pcis": ["Environmental Education"],
                            "values": ["Creativity"]
                        }
                    ]
                }
            ]
        }
    ]
}

# Continue with more subjects in the next part...
# This file will be continued with Computer Science, Fasihi ya Kiswahili, 
# History and Citizenship, and Home Science data

print("Agriculture data structure defined successfully")
print(f"Strands: {len(AGRICULTURE_DATA['strands'])}")
for strand in AGRICULTURE_DATA['strands']:
    print(f"  - {strand['name']}: {len(strand['substrands'])} substrands")
    total_slos = sum(len(ss['slos']) for ss in strand['substrands'])
    print(f"    Total SLOs: {total_slos}")
