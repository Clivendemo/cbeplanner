#!/usr/bin/env python3
"""
Seed curriculum data for multiple subjects including:
- Core Competencies
- Core Values  
- Pertinent and Contemporary Issues (PCIs)
- Subject-specific strands, substrands, and SLOs
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# ============================================
# CORE COMPETENCIES (CBC Kenya)
# ============================================
CORE_COMPETENCIES = [
    {"name": "Communication and Collaboration", "description": "Ability to communicate effectively and work collaboratively with others in diverse settings."},
    {"name": "Critical Thinking and Problem Solving", "description": "Ability to analyze information, evaluate evidence, and solve problems creatively."},
    {"name": "Creativity and Imagination", "description": "Ability to generate new ideas, think innovatively, and approach challenges with creativity."},
    {"name": "Citizenship", "description": "Understanding of rights and responsibilities as a citizen and active participation in community affairs."},
    {"name": "Digital Literacy", "description": "Ability to use digital tools and technologies effectively and responsibly."},
    {"name": "Learning to Learn", "description": "Ability to take responsibility for own learning and continuously seek knowledge and skills."},
    {"name": "Self-Efficacy", "description": "Confidence in one's ability to succeed and achieve goals through effort and persistence."}
]

# ============================================
# CORE VALUES (CBC Kenya)
# ============================================
CORE_VALUES = [
    {"name": "Love", "description": "Showing care, compassion, and kindness to self and others."},
    {"name": "Responsibility", "description": "Being accountable for one's actions and fulfilling obligations."},
    {"name": "Respect", "description": "Showing consideration and regard for oneself, others, and the environment."},
    {"name": "Unity", "description": "Working together harmoniously for common goals and national cohesion."},
    {"name": "Peace", "description": "Promoting harmony, tolerance, and non-violent resolution of conflicts."},
    {"name": "Patriotism", "description": "Love for one's country and commitment to national development."},
    {"name": "Social Justice", "description": "Fairness and equity in the distribution of resources and opportunities."},
    {"name": "Integrity", "description": "Honesty, truthfulness, and adherence to moral and ethical principles."}
]

# ============================================
# PERTINENT AND CONTEMPORARY ISSUES (PCIs)
# ============================================
PCIS = [
    {"name": "Environmental Conservation", "description": "Protection and sustainable management of natural resources and ecosystems."},
    {"name": "Safety and Security", "description": "Personal safety, road safety, and security awareness in various contexts."},
    {"name": "Health Education", "description": "Physical and mental health promotion, disease prevention, and healthy lifestyles."},
    {"name": "Life Skills", "description": "Essential skills for daily living including decision-making, coping, and self-management."},
    {"name": "Financial Literacy", "description": "Understanding of money management, savings, investments, and economic concepts."},
    {"name": "Citizenship Education", "description": "Rights, responsibilities, and participation in democratic processes."},
    {"name": "Gender Issues", "description": "Gender equality, equity, and addressing gender-based discrimination."},
    {"name": "Drug and Substance Abuse", "description": "Prevention and awareness of harmful effects of drugs and substances."},
    {"name": "Disaster Risk Reduction", "description": "Preparedness, response, and mitigation of natural and man-made disasters."},
    {"name": "Animal Welfare", "description": "Ethical treatment and care of animals in various contexts."},
    {"name": "Digital Citizenship", "description": "Responsible and ethical use of technology and online platforms."},
    {"name": "Climate Change", "description": "Understanding and addressing the causes and effects of climate change."}
]

# ============================================
# SUBJECT DATA
# ============================================

AGRICULTURE_DATA = {
    "name": "Agriculture",
    "strands": [
        {
            "name": "Crop Production",
            "substrands": [
                {
                    "name": "Agricultural Land",
                    "slos": [
                        {"name": "Describe ways of accessing land for agricultural use", "description": "Learner should be able to describe various methods of acquiring land for farming including leasing, purchasing, and communal ownership."},
                        {"name": "Evaluate land utility for agricultural production", "description": "Learner should be able to assess land suitability for different agricultural activities."},
                        {"name": "Analyze natural factors determining land productivity", "description": "Learner should be able to analyze factors like soil type, climate, and topography affecting agricultural productivity."}
                    ],
                    "competencies": ["Critical Thinking and Problem Solving", "Communication and Collaboration"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Environmental Conservation", "Financial Literacy"]
                },
                {
                    "name": "Properties of Soil",
                    "slos": [
                        {"name": "Describe properties of soil for crop production", "description": "Learner should be able to explain soil texture, structure, porosity, and water-holding capacity."},
                        {"name": "Investigate soil properties for crop production", "description": "Learner should be able to conduct experiments to determine soil properties."},
                        {"name": "Relate soil profile importance to crop production", "description": "Learner should be able to explain how different soil horizons affect plant growth."}
                    ],
                    "competencies": ["Critical Thinking and Problem Solving", "Creativity and Imagination"],
                    "values": ["Responsibility", "Respect"],
                    "pcis": ["Environmental Conservation", "Life Skills"]
                },
                {
                    "name": "Land Preparation",
                    "slos": [
                        {"name": "Describe fallow land preparation activities", "description": "Learner should be able to explain bush clearing, ploughing, harrowing, and seedbed preparation."},
                        {"name": "Carry out land preparation operations", "description": "Learner should be able to practically prepare land for selected crops."},
                        {"name": "Apply conservation tillage in crop production", "description": "Learner should be able to implement minimum tillage and mulching practices."}
                    ],
                    "competencies": ["Self-Efficacy", "Learning to Learn"],
                    "values": ["Responsibility", "Love"],
                    "pcis": ["Environmental Conservation", "Climate Change"]
                },
                {
                    "name": "Field Management Practices",
                    "slos": [
                        {"name": "Describe management practices of selected crops", "description": "Learner should be able to explain pruning, top dressing, and pest control for vegetables and perennials."},
                        {"name": "Carry out selected management practices", "description": "Learner should be able to practically perform crop management activities."}
                    ],
                    "competencies": ["Self-Efficacy", "Critical Thinking and Problem Solving"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Life Skills", "Financial Literacy"]
                },
                {
                    "name": "Crop Protection",
                    "slos": [
                        {"name": "Identify weeds in a crop field", "description": "Learner should be able to recognize common weeds and their characteristics."},
                        {"name": "Classify weeds based on provided criteria", "description": "Learner should be able to categorize weeds by life cycle, morphology, and habitat."},
                        {"name": "Describe methods of weed control", "description": "Learner should be able to explain cultural, mechanical, chemical, and biological weed control methods."}
                    ],
                    "competencies": ["Critical Thinking and Problem Solving", "Digital Literacy"],
                    "values": ["Responsibility", "Respect"],
                    "pcis": ["Environmental Conservation", "Health Education"]
                }
            ]
        },
        {
            "name": "Animal Production",
            "substrands": [
                {
                    "name": "Breeds of Livestock",
                    "slos": [
                        {"name": "Describe breeds of livestock based on uses", "description": "Learner should be able to classify cattle, pigs, sheep, goats, and rabbits by their primary uses."},
                        {"name": "Distinguish livestock breeds by characteristics", "description": "Learner should be able to identify breeds by their physical and productive characteristics."}
                    ],
                    "competencies": ["Communication and Collaboration", "Learning to Learn"],
                    "values": ["Respect", "Love"],
                    "pcis": ["Animal Welfare", "Financial Literacy"]
                },
                {
                    "name": "Animal Handling and Safety",
                    "slos": [
                        {"name": "Examine forms of animal handling", "description": "Learner should be able to describe proper techniques for handling different livestock."},
                        {"name": "Describe structures for safe animal handling", "description": "Learner should be able to explain crushes, pens, and other handling facilities."},
                        {"name": "Use tools for safe animal handling", "description": "Learner should be able to properly use halters, ropes, and restraint equipment."}
                    ],
                    "competencies": ["Self-Efficacy", "Critical Thinking and Problem Solving"],
                    "values": ["Responsibility", "Love"],
                    "pcis": ["Animal Welfare", "Safety and Security"]
                },
                {
                    "name": "General Animal Health",
                    "slos": [
                        {"name": "Explain benefits of keeping animals healthy", "description": "Learner should be able to describe how animal health affects productivity and farm income."},
                        {"name": "Identify signs of ill health in livestock", "description": "Learner should be able to recognize symptoms of common livestock diseases."},
                        {"name": "Propose control measures for livestock diseases", "description": "Learner should be able to suggest preventive and curative measures for animal diseases."}
                    ],
                    "competencies": ["Critical Thinking and Problem Solving", "Communication and Collaboration"],
                    "values": ["Love", "Responsibility"],
                    "pcis": ["Animal Welfare", "Health Education"]
                },
                {
                    "name": "Bee Keeping",
                    "slos": [
                        {"name": "Explain factors in siting an apiary", "description": "Learner should be able to describe considerations for apiary location including water, forage, and security."},
                        {"name": "Describe the process of stocking a hive", "description": "Learner should be able to explain methods of acquiring and introducing bee colonies."},
                        {"name": "Demonstrate honey harvesting process", "description": "Learner should be able to safely harvest and process honey."}
                    ],
                    "competencies": ["Creativity and Imagination", "Self-Efficacy"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Environmental Conservation", "Financial Literacy"]
                }
            ]
        },
        {
            "name": "Agricultural Technologies and Entrepreneurship",
            "substrands": [
                {
                    "name": "Tools and Equipment",
                    "slos": [
                        {"name": "Identify agricultural tools and equipment", "description": "Learner should be able to recognize various tools used in different agricultural tasks."},
                        {"name": "Carry out tasks using appropriate tools", "description": "Learner should be able to use tools correctly for specific agricultural operations."},
                        {"name": "Maintain agricultural tools and equipment", "description": "Learner should be able to clean, store, and repair tools properly."}
                    ],
                    "competencies": ["Self-Efficacy", "Learning to Learn"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Safety and Security", "Life Skills"]
                },
                {
                    "name": "Product Processing and Value Addition",
                    "slos": [
                        {"name": "Suggest value addition methods for produce", "description": "Learner should be able to identify opportunities for adding value to agricultural products."},
                        {"name": "Process agricultural produce of plant origin", "description": "Learner should be able to process fruits, vegetables, and grains."},
                        {"name": "Process agricultural produce of animal origin", "description": "Learner should be able to process milk, meat, and honey."},
                        {"name": "Carry out packaging and branding", "description": "Learner should be able to package and brand processed agricultural products."}
                    ],
                    "competencies": ["Creativity and Imagination", "Digital Literacy"],
                    "values": ["Integrity", "Responsibility"],
                    "pcis": ["Financial Literacy", "Health Education"]
                },
                {
                    "name": "Establishing Agricultural Enterprise",
                    "slos": [
                        {"name": "Explain factors of production", "description": "Learner should be able to describe land, labor, capital, and entrepreneurship in agriculture."},
                        {"name": "Propose ways of acquiring capital", "description": "Learner should be able to identify sources of funding for agricultural ventures."},
                        {"name": "Examine factors in selecting an enterprise", "description": "Learner should be able to analyze market demand, resources, and profitability."}
                    ],
                    "competencies": ["Critical Thinking and Problem Solving", "Self-Efficacy"],
                    "values": ["Integrity", "Responsibility"],
                    "pcis": ["Financial Literacy", "Citizenship Education"]
                }
            ]
        }
    ]
}

BIOLOGY_DATA = {
    "name": "Biology",
    "strands": [
        {
            "name": "Cell Biology and Biodiversity",
            "substrands": [
                {
                    "name": "Introduction to Biology",
                    "slos": [
                        {"name": "Explain application of Biology in everyday life", "description": "Learner should be able to describe how biological knowledge applies to medicine, agriculture, and environment."},
                        {"name": "Relate Biology fields to career opportunities", "description": "Learner should be able to identify careers in medicine, research, conservation, and biotechnology."}
                    ],
                    "competencies": ["Communication and Collaboration", "Learning to Learn"],
                    "values": ["Love", "Responsibility"],
                    "pcis": ["Health Education", "Citizenship Education"]
                },
                {
                    "name": "Specimen Collection and Preservation",
                    "slos": [
                        {"name": "Identify apparatus for specimen collection", "description": "Learner should be able to recognize nets, jars, forceps, and preservation materials."},
                        {"name": "Collect and preserve biological specimens", "description": "Learner should be able to safely collect, process, and preserve plant and animal specimens."}
                    ],
                    "competencies": ["Self-Efficacy", "Critical Thinking and Problem Solving"],
                    "values": ["Responsibility", "Respect"],
                    "pcis": ["Environmental Conservation", "Safety and Security"]
                },
                {
                    "name": "Cell Structure and Specialization",
                    "slos": [
                        {"name": "Differentiate between light and electron microscopes", "description": "Learner should be able to compare the features and uses of different microscope types."},
                        {"name": "Describe structure of plant and animal cells", "description": "Learner should be able to identify and explain functions of cell organelles."},
                        {"name": "Prepare temporary microscope slides", "description": "Learner should be able to prepare and observe cell specimens under microscope."},
                        {"name": "Relate specialized cell structures to functions", "description": "Learner should be able to explain adaptations of nerve, muscle, and root hair cells."}
                    ],
                    "competencies": ["Critical Thinking and Problem Solving", "Digital Literacy"],
                    "values": ["Integrity", "Responsibility"],
                    "pcis": ["Health Education", "Life Skills"]
                },
                {
                    "name": "Chemicals of Life",
                    "slos": [
                        {"name": "Describe composition of chemicals of life", "description": "Learner should be able to explain structure and functions of carbohydrates, proteins, lipids, and vitamins."},
                        {"name": "Investigate presence of food nutrients", "description": "Learner should be able to conduct food tests for carbohydrates, proteins, lipids, and vitamin C."},
                        {"name": "Determine factors affecting enzyme reactions", "description": "Learner should be able to investigate effects of temperature, pH, and concentration on enzymes."}
                    ],
                    "competencies": ["Critical Thinking and Problem Solving", "Creativity and Imagination"],
                    "values": ["Integrity", "Responsibility"],
                    "pcis": ["Health Education", "Life Skills"]
                }
            ]
        },
        {
            "name": "Anatomy and Physiology of Plants",
            "substrands": [
                {
                    "name": "Plant Nutrition",
                    "slos": [
                        {"name": "Describe types of nutrition in plants", "description": "Learner should be able to explain autotrophic and heterotrophic nutrition."},
                        {"name": "Relate chloroplast structure to function", "description": "Learner should be able to explain how chloroplast structure facilitates photosynthesis."},
                        {"name": "Illustrate photosynthesis light and dark stages", "description": "Learner should be able to describe the biochemical processes of photosynthesis."}
                    ],
                    "competencies": ["Critical Thinking and Problem Solving", "Learning to Learn"],
                    "values": ["Responsibility", "Love"],
                    "pcis": ["Environmental Conservation", "Climate Change"]
                },
                {
                    "name": "Plant Transport",
                    "slos": [
                        {"name": "Relate plant transport structures to functions", "description": "Learner should be able to explain how xylem and phloem facilitate transport."},
                        {"name": "Illustrate vascular tissue arrangement", "description": "Learner should be able to compare vascular bundles in monocots and dicots."},
                        {"name": "Demonstrate water and mineral uptake", "description": "Learner should be able to conduct experiments on root pressure and transpiration."}
                    ],
                    "competencies": ["Self-Efficacy", "Critical Thinking and Problem Solving"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Environmental Conservation", "Life Skills"]
                },
                {
                    "name": "Plant Gaseous Exchange and Respiration",
                    "slos": [
                        {"name": "Relate gaseous exchange structures to function", "description": "Learner should be able to explain how stomata and lenticels facilitate gas exchange."},
                        {"name": "Describe stomata opening and closing mechanism", "description": "Learner should be able to explain guard cell function and factors affecting stomatal movement."},
                        {"name": "Investigate aerobic and anaerobic respiration", "description": "Learner should be able to conduct experiments demonstrating respiration processes."}
                    ],
                    "competencies": ["Critical Thinking and Problem Solving", "Self-Efficacy"],
                    "values": ["Responsibility", "Respect"],
                    "pcis": ["Environmental Conservation", "Health Education"]
                }
            ]
        },
        {
            "name": "Anatomy and Physiology of Animals",
            "substrands": [
                {
                    "name": "Animal Nutrition",
                    "slos": [
                        {"name": "Relate insect mouthpart structure to function", "description": "Learner should be able to explain adaptations of biting, sucking, and piercing mouthparts."},
                        {"name": "Relate bird beak structure to function", "description": "Learner should be able to explain beak adaptations for different feeding modes."}
                    ],
                    "competencies": ["Critical Thinking and Problem Solving", "Learning to Learn"],
                    "values": ["Love", "Respect"],
                    "pcis": ["Animal Welfare", "Environmental Conservation"]
                },
                {
                    "name": "Animal Transport",
                    "slos": [
                        {"name": "Explain importance of transport in animals", "description": "Learner should be able to describe how transport systems distribute nutrients, gases, and wastes."},
                        {"name": "Illustrate transport systems in different animals", "description": "Learner should be able to compare circulatory systems in insects, fish, amphibians, reptiles, and mammals."},
                        {"name": "Describe mammalian heart pumping mechanism", "description": "Learner should be able to explain the cardiac cycle and blood flow through the heart."},
                        {"name": "Explain blood grouping systems", "description": "Learner should be able to describe ABO and Rhesus factor blood groups and their significance."}
                    ],
                    "competencies": ["Critical Thinking and Problem Solving", "Communication and Collaboration"],
                    "values": ["Responsibility", "Love"],
                    "pcis": ["Health Education", "Life Skills"]
                },
                {
                    "name": "Animal Gaseous Exchange and Respiration",
                    "slos": [
                        {"name": "Explain characteristics of respiratory surfaces", "description": "Learner should be able to describe features like thin walls, moist surface, and large surface area."},
                        {"name": "Describe respiratory structure adaptations", "description": "Learner should be able to explain adaptations of gills, lungs, and tracheal systems."},
                        {"name": "Describe gaseous exchange mechanism in humans", "description": "Learner should be able to explain breathing movements and gas exchange in alveoli."},
                        {"name": "Calculate respiratory quotient", "description": "Learner should be able to determine RQ values for different substrates."}
                    ],
                    "competencies": ["Critical Thinking and Problem Solving", "Self-Efficacy"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Health Education", "Life Skills"]
                }
            ]
        }
    ]
}

ARABIC_DATA = {
    "name": "Arabic",
    "strands": [
        {
            "name": "Listening and Speaking",
            "substrands": [
                {
                    "name": "Listening Comprehension",
                    "slos": [
                        {"name": "Understand spoken Arabic in various contexts", "description": "Learner should be able to comprehend Arabic speech in formal and informal settings."},
                        {"name": "Identify main ideas in spoken Arabic", "description": "Learner should be able to extract key information from Arabic conversations and speeches."}
                    ],
                    "competencies": ["Communication and Collaboration", "Learning to Learn"],
                    "values": ["Respect", "Unity"],
                    "pcis": ["Citizenship Education", "Life Skills"]
                },
                {
                    "name": "Oral Expression",
                    "slos": [
                        {"name": "Express ideas clearly in Arabic", "description": "Learner should be able to communicate thoughts and opinions in correct Arabic."},
                        {"name": "Participate in Arabic conversations", "description": "Learner should be able to engage in discussions on various topics in Arabic."}
                    ],
                    "competencies": ["Communication and Collaboration", "Self-Efficacy"],
                    "values": ["Respect", "Love"],
                    "pcis": ["Life Skills", "Citizenship Education"]
                }
            ]
        },
        {
            "name": "Reading",
            "substrands": [
                {
                    "name": "Reading Comprehension",
                    "slos": [
                        {"name": "Read Arabic texts with comprehension", "description": "Learner should be able to understand written Arabic passages and extract meaning."},
                        {"name": "Analyze Arabic literary texts", "description": "Learner should be able to interpret themes, styles, and messages in Arabic literature."}
                    ],
                    "competencies": ["Critical Thinking and Problem Solving", "Learning to Learn"],
                    "values": ["Love", "Integrity"],
                    "pcis": ["Life Skills", "Citizenship Education"]
                },
                {
                    "name": "Vocabulary Development",
                    "slos": [
                        {"name": "Build Arabic vocabulary", "description": "Learner should be able to expand Arabic word knowledge through reading and context."},
                        {"name": "Use Arabic vocabulary appropriately", "description": "Learner should be able to apply learned vocabulary in speaking and writing."}
                    ],
                    "competencies": ["Learning to Learn", "Communication and Collaboration"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Life Skills", "Digital Citizenship"]
                }
            ]
        },
        {
            "name": "Writing",
            "substrands": [
                {
                    "name": "Composition Writing",
                    "slos": [
                        {"name": "Write coherent Arabic compositions", "description": "Learner should be able to compose essays, letters, and reports in Arabic."},
                        {"name": "Apply Arabic grammar in writing", "description": "Learner should be able to use correct grammatical structures in written Arabic."}
                    ],
                    "competencies": ["Creativity and Imagination", "Communication and Collaboration"],
                    "values": ["Integrity", "Responsibility"],
                    "pcis": ["Life Skills", "Digital Citizenship"]
                }
            ]
        }
    ]
}

AVIATION_TECHNOLOGY_DATA = {
    "name": "Aviation Technology",
    "strands": [
        {
            "name": "Introduction to Aviation",
            "substrands": [
                {
                    "name": "History of Aviation",
                    "slos": [
                        {"name": "Trace the development of aviation", "description": "Learner should be able to describe key milestones in aviation history from early flight to modern aircraft."},
                        {"name": "Identify pioneers in aviation", "description": "Learner should be able to recognize contributions of aviation pioneers like the Wright Brothers."}
                    ],
                    "competencies": ["Learning to Learn", "Communication and Collaboration"],
                    "values": ["Patriotism", "Respect"],
                    "pcis": ["Citizenship Education", "Life Skills"]
                },
                {
                    "name": "Types of Aircraft",
                    "slos": [
                        {"name": "Classify aircraft by type and function", "description": "Learner should be able to categorize fixed-wing, rotary-wing, and other aircraft types."},
                        {"name": "Describe aircraft components", "description": "Learner should be able to identify and explain functions of major aircraft parts."}
                    ],
                    "competencies": ["Critical Thinking and Problem Solving", "Digital Literacy"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Safety and Security", "Environmental Conservation"]
                }
            ]
        },
        {
            "name": "Principles of Flight",
            "substrands": [
                {
                    "name": "Aerodynamics",
                    "slos": [
                        {"name": "Explain forces acting on aircraft", "description": "Learner should be able to describe lift, drag, thrust, and weight in flight."},
                        {"name": "Apply Bernoulli's principle to flight", "description": "Learner should be able to explain how airfoil shape creates lift."}
                    ],
                    "competencies": ["Critical Thinking and Problem Solving", "Self-Efficacy"],
                    "values": ["Integrity", "Responsibility"],
                    "pcis": ["Life Skills", "Safety and Security"]
                },
                {
                    "name": "Aircraft Control",
                    "slos": [
                        {"name": "Describe aircraft control surfaces", "description": "Learner should be able to explain functions of ailerons, elevators, and rudder."},
                        {"name": "Explain aircraft movement along axes", "description": "Learner should be able to describe pitch, roll, and yaw movements."}
                    ],
                    "competencies": ["Self-Efficacy", "Critical Thinking and Problem Solving"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Safety and Security", "Life Skills"]
                }
            ]
        },
        {
            "name": "Aviation Safety and Regulations",
            "substrands": [
                {
                    "name": "Aviation Safety",
                    "slos": [
                        {"name": "Explain aviation safety procedures", "description": "Learner should be able to describe pre-flight checks, emergency procedures, and safety equipment."},
                        {"name": "Identify aviation safety regulations", "description": "Learner should be able to recognize rules and standards governing aviation safety."}
                    ],
                    "competencies": ["Citizenship", "Self-Efficacy"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Safety and Security", "Disaster Risk Reduction"]
                }
            ]
        }
    ]
}

BUILDING_CONSTRUCTION_DATA = {
    "name": "Building Construction",
    "strands": [
        {
            "name": "Construction Materials",
            "substrands": [
                {
                    "name": "Types of Building Materials",
                    "slos": [
                        {"name": "Identify common building materials", "description": "Learner should be able to recognize cement, sand, aggregates, timber, and steel."},
                        {"name": "Describe properties of building materials", "description": "Learner should be able to explain strength, durability, and workability of materials."}
                    ],
                    "competencies": ["Critical Thinking and Problem Solving", "Learning to Learn"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Environmental Conservation", "Safety and Security"]
                },
                {
                    "name": "Material Selection and Testing",
                    "slos": [
                        {"name": "Select appropriate building materials", "description": "Learner should be able to choose materials based on purpose, cost, and availability."},
                        {"name": "Conduct basic material tests", "description": "Learner should be able to perform simple tests for material quality."}
                    ],
                    "competencies": ["Self-Efficacy", "Critical Thinking and Problem Solving"],
                    "values": ["Integrity", "Responsibility"],
                    "pcis": ["Financial Literacy", "Safety and Security"]
                }
            ]
        },
        {
            "name": "Building Techniques",
            "substrands": [
                {
                    "name": "Foundation Construction",
                    "slos": [
                        {"name": "Describe types of foundations", "description": "Learner should be able to explain strip, pad, raft, and pile foundations."},
                        {"name": "Carry out foundation setting out", "description": "Learner should be able to mark out foundation dimensions accurately."}
                    ],
                    "competencies": ["Self-Efficacy", "Critical Thinking and Problem Solving"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Safety and Security", "Life Skills"]
                },
                {
                    "name": "Wall Construction",
                    "slos": [
                        {"name": "Describe wall construction methods", "description": "Learner should be able to explain brick, block, and stone masonry techniques."},
                        {"name": "Construct walls using appropriate techniques", "description": "Learner should be able to build walls with proper bonding and jointing."}
                    ],
                    "competencies": ["Self-Efficacy", "Creativity and Imagination"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Safety and Security", "Life Skills"]
                }
            ]
        },
        {
            "name": "Building Services",
            "substrands": [
                {
                    "name": "Plumbing Basics",
                    "slos": [
                        {"name": "Identify plumbing components", "description": "Learner should be able to recognize pipes, fittings, and fixtures."},
                        {"name": "Carry out basic plumbing installations", "description": "Learner should be able to connect pipes and install simple fixtures."}
                    ],
                    "competencies": ["Self-Efficacy", "Learning to Learn"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Health Education", "Environmental Conservation"]
                },
                {
                    "name": "Electrical Basics",
                    "slos": [
                        {"name": "Identify electrical components", "description": "Learner should be able to recognize cables, switches, and outlets."},
                        {"name": "Explain electrical safety measures", "description": "Learner should be able to describe precautions when working with electricity."}
                    ],
                    "competencies": ["Self-Efficacy", "Critical Thinking and Problem Solving"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Safety and Security", "Life Skills"]
                }
            ]
        }
    ]
}

ALL_SUBJECTS = [AGRICULTURE_DATA, BIOLOGY_DATA, ARABIC_DATA, AVIATION_TECHNOLOGY_DATA, BUILDING_CONSTRUCTION_DATA]


async def seed_core_data():
    """Seed core competencies, values, and PCIs"""
    print("\n=== Seeding Core Data ===")
    
    # Seed Competencies
    competencies_added = 0
    for comp in CORE_COMPETENCIES:
        existing = await db.competencies.find_one({"name": comp["name"]})
        if not existing:
            await db.competencies.insert_one(comp)
            competencies_added += 1
    print(f"Core Competencies added: {competencies_added}")
    
    # Seed Values
    values_added = 0
    for val in CORE_VALUES:
        existing = await db.values.find_one({"name": val["name"]})
        if not existing:
            await db.values.insert_one(val)
            values_added += 1
    print(f"Core Values added: {values_added}")
    
    # Seed PCIs
    pcis_added = 0
    for pci in PCIS:
        existing = await db.pcis.find_one({"name": pci["name"]})
        if not existing:
            await db.pcis.insert_one(pci)
            pcis_added += 1
    print(f"PCIs added: {pcis_added}")
    
    return competencies_added, values_added, pcis_added


async def get_or_create_grade():
    """Get or create Grade 10"""
    grade = await db.grades.find_one({"name": {"$regex": "10|Ten", "$options": "i"}})
    if not grade:
        result = await db.grades.insert_one({"name": "Grade 10", "order": 10})
        return str(result.inserted_id)
    return str(grade["_id"])


async def get_id_by_name(collection_name, name):
    """Get document ID by name"""
    doc = await db[collection_name].find_one({"name": name})
    return str(doc["_id"]) if doc else None


async def seed_subject(subject_data, grade_id):
    """Seed a single subject with all its data"""
    subject_name = subject_data["name"]
    print(f"\n--- Seeding {subject_name} ---")
    
    # Check/create subject
    subject = await db.subjects.find_one({"name": subject_name})
    if not subject:
        result = await db.subjects.insert_one({
            "name": subject_name,
            "gradeIds": [grade_id]
        })
        subject_id = str(result.inserted_id)
        print(f"  Created subject: {subject_name}")
    else:
        subject_id = str(subject["_id"])
        if grade_id not in subject.get("gradeIds", []):
            await db.subjects.update_one(
                {"_id": subject["_id"]},
                {"$addToSet": {"gradeIds": grade_id}}
            )
        print(f"  Found existing subject: {subject_name}")
    
    strands_count = 0
    substrands_count = 0
    slos_count = 0
    mappings_count = 0
    
    for strand_data in subject_data["strands"]:
        # Create/get strand
        strand = await db.strands.find_one({
            "name": strand_data["name"],
            "subjectId": subject_id
        })
        if not strand:
            result = await db.strands.insert_one({
                "name": strand_data["name"],
                "subjectId": subject_id
            })
            strand_id = str(result.inserted_id)
            strands_count += 1
        else:
            strand_id = str(strand["_id"])
        
        for substrand_data in strand_data["substrands"]:
            # Create/get substrand
            substrand = await db.substrands.find_one({
                "name": substrand_data["name"],
                "strandId": strand_id
            })
            if not substrand:
                result = await db.substrands.insert_one({
                    "name": substrand_data["name"],
                    "strandId": strand_id
                })
                substrand_id = str(result.inserted_id)
                substrands_count += 1
            else:
                substrand_id = str(substrand["_id"])
            
            # Get competency, value, and PCI IDs for this substrand
            competency_ids = []
            for comp_name in substrand_data.get("competencies", []):
                comp_id = await get_id_by_name("competencies", comp_name)
                if comp_id:
                    competency_ids.append(comp_id)
            
            value_ids = []
            for val_name in substrand_data.get("values", []):
                val_id = await get_id_by_name("values", val_name)
                if val_id:
                    value_ids.append(val_id)
            
            pci_ids = []
            for pci_name in substrand_data.get("pcis", []):
                pci_id = await get_id_by_name("pcis", pci_name)
                if pci_id:
                    pci_ids.append(pci_id)
            
            # Create SLOs and mappings
            for slo_data in substrand_data["slos"]:
                slo = await db.slos.find_one({
                    "name": slo_data["name"],
                    "substrandId": substrand_id
                })
                if not slo:
                    result = await db.slos.insert_one({
                        "name": slo_data["name"],
                        "description": slo_data["description"],
                        "substrandId": substrand_id
                    })
                    slo_id = str(result.inserted_id)
                    slos_count += 1
                    
                    # Create SLO mapping with competencies, values, and PCIs
                    if competency_ids or value_ids or pci_ids:
                        await db.slo_mappings.insert_one({
                            "sloId": slo_id,
                            "competencyIds": competency_ids,
                            "valueIds": value_ids,
                            "pciIds": pci_ids,
                            "assessmentIds": []
                        })
                        mappings_count += 1
    
    print(f"  Strands: {strands_count}, Substrands: {substrands_count}, SLOs: {slos_count}, Mappings: {mappings_count}")
    return strands_count, substrands_count, slos_count, mappings_count


async def main():
    """Main seeding function"""
    print("=" * 50)
    print("CURRICULUM DATA SEEDING")
    print("=" * 50)
    
    # Seed core data first
    await seed_core_data()
    
    # Get/create Grade 10
    grade_id = await get_or_create_grade()
    print(f"\nGrade 10 ID: {grade_id}")
    
    # Seed all subjects
    total_strands = 0
    total_substrands = 0
    total_slos = 0
    total_mappings = 0
    
    for subject_data in ALL_SUBJECTS:
        strands, substrands, slos, mappings = await seed_subject(subject_data, grade_id)
        total_strands += strands
        total_substrands += substrands
        total_slos += slos
        total_mappings += mappings
    
    print("\n" + "=" * 50)
    print("SEEDING COMPLETE")
    print("=" * 50)
    print(f"Total Strands: {total_strands}")
    print(f"Total Substrands: {total_substrands}")
    print(f"Total SLOs: {total_slos}")
    print(f"Total SLO Mappings: {total_mappings}")
    
    # Verify counts
    print("\n=== Database Totals ===")
    print(f"Subjects: {await db.subjects.count_documents({})}")
    print(f"Strands: {await db.strands.count_documents({})}")
    print(f"Substrands: {await db.substrands.count_documents({})}")
    print(f"SLOs: {await db.slos.count_documents({})}")
    print(f"Competencies: {await db.competencies.count_documents({})}")
    print(f"Values: {await db.values.count_documents({})}")
    print(f"PCIs: {await db.pcis.count_documents({})}")
    print(f"SLO Mappings: {await db.slo_mappings.count_documents({})}")


if __name__ == "__main__":
    asyncio.run(main())
