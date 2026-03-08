#!/usr/bin/env python3
"""
Grade 7 Complete Curriculum Seeding Script
==========================================
Seeds Grade 7 curriculum data extracted from official KICD PDFs.
Includes: Strands, Substrands, SLOs, and SLO Mappings.

PDFs processed:
- GRADE.7.ENGLISH.pdf
- GRADE.7.MATHEMATICS.pdf
- GRADE.7.INTEGRATED.SCIENCE.pdf
- Kiswahili-Grade-7-.pdf
- Social-Studies-Grade-7-Formatted-April-2024.pdf
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from datetime import datetime

# Database connection
mongo_url = os.environ.get('MONGODB_URI') or os.environ.get('MONGO_URL')
if not mongo_url:
    raise ValueError("MONGODB_URI or MONGO_URL environment variable is required")
client = AsyncIOMotorClient(mongo_url)
db = client['cbeplanner']

# ============================================================================
# MATHEMATICS GRADE 7 - Extracted from GRADE.7.MATHEMATICS.pdf
# ============================================================================
MATHEMATICS_GRADE_7 = {
    "name": "Mathematics",
    "strands": [
        {
            "name": "Numbers",
            "substrands": [
                {
                    "name": "Whole Numbers",
                    "slos": [
                        {"name": "use place value and total value of digits up to hundreds of millions in real life"},
                        {"name": "read and write numbers in symbols up to hundreds of millions in real life situations"},
                        {"name": "read and write numbers in words up to millions for fluency"},
                        {"name": "round off numbers up to the nearest hundreds of millions in real life situations"},
                        {"name": "classify natural numbers as even, odd and prime in different situations"},
                        {"name": "apply operations of whole numbers in real life situations"},
                        {"name": "identify number sequence in different situations"},
                        {"name": "create number sequence for playing number games"},
                        {"name": "appreciate use of whole numbers in real life situations"},
                    ],
                    "learning_experiences": "identify and write place value and total value of digits using place value apparatus, read and write numbers in symbols on number cards or charts, prepare and use place value charts to round off numbers, play number games and sort numbers as even odd or prime, work out combined operations in the correct order, identify number patterns to work out number sequences",
                    "inquiry_questions": ["Why do we write numbers in words and/or symbols?", "Where do we write numbers in words or symbols?"],
                    "core_competencies": ["Communication and collaboration", "Critical thinking and problem solving", "Creativity and Imagination"],
                    "values": ["Respect", "Unity", "Peace"],
                    "pcis": ["Financial literacy"]
                },
                {
                    "name": "Factors",
                    "slos": [
                        {"name": "work out factors of numbers in different situations"},
                        {"name": "express numbers as products of prime factors in different situations"},
                        {"name": "work out the GCD of numbers by factor method in different situations"},
                        {"name": "work out the GCD of numbers by prime factorization in different situations"},
                        {"name": "apply GCD in real life situations"},
                    ],
                    "learning_experiences": "list and work out factors of given numbers, express numbers as products of prime factors, determine the GCD of numbers using factor method and prime factorization",
                    "inquiry_questions": ["How do we identify factors of numbers?", "Where do we apply GCD in daily activities?"],
                    "core_competencies": ["Critical thinking and problem solving", "Learning to learn"],
                    "values": ["Responsibility", "Respect"],
                    "pcis": ["Financial literacy"]
                },
                {
                    "name": "Multiples",
                    "slos": [
                        {"name": "list multiples of numbers in different situations"},
                        {"name": "work out common multiples of numbers in different situations"},
                        {"name": "work out the LCM of numbers by listing multiples in different situations"},
                        {"name": "work out the LCM of numbers by prime factorization in different situations"},
                        {"name": "apply LCM in real life situations"},
                    ],
                    "learning_experiences": "list multiples of given numbers, identify common multiples, determine LCM using listing and prime factorization methods",
                    "inquiry_questions": ["How do we identify multiples of numbers?", "Where do we apply LCM in daily activities?"],
                    "core_competencies": ["Critical thinking and problem solving", "Creativity and Imagination"],
                    "values": ["Unity", "Respect"],
                    "pcis": ["Financial literacy"]
                },
                {
                    "name": "Fractions",
                    "slos": [
                        {"name": "identify types of fractions in different situations"},
                        {"name": "convert improper fractions to mixed numbers and vice versa"},
                        {"name": "work out equivalent fractions in different situations"},
                        {"name": "compare and order fractions in different situations"},
                        {"name": "work out operations on fractions in real life situations"},
                        {"name": "apply operations on fractions in real life situations"},
                    ],
                    "learning_experiences": "identify and classify proper, improper and mixed fractions, convert between improper fractions and mixed numbers, work out equivalent fractions, compare and order fractions, perform operations on fractions",
                    "inquiry_questions": ["How do we identify different types of fractions?", "Where do we use fractions in real life?"],
                    "core_competencies": ["Communication and collaboration", "Critical thinking and problem solving"],
                    "values": ["Responsibility", "Unity"],
                    "pcis": ["Financial literacy"]
                },
                {
                    "name": "Decimals",
                    "slos": [
                        {"name": "identify place value and total value of digits in decimals in different situations"},
                        {"name": "convert fractions to decimals and vice versa in different situations"},
                        {"name": "compare and order decimals in different situations"},
                        {"name": "work out operations on decimals in real life situations"},
                        {"name": "round off decimals to a given number of decimal places in different situations"},
                    ],
                    "learning_experiences": "identify place value of digits in decimals, convert between fractions and decimals, compare and order decimals, perform operations on decimals, round off decimals",
                    "inquiry_questions": ["How do we convert fractions to decimals?", "Where do we use decimals in real life?"],
                    "core_competencies": ["Critical thinking and problem solving", "Digital literacy"],
                    "values": ["Integrity", "Responsibility"],
                    "pcis": ["Financial literacy"]
                },
                {
                    "name": "Squares and Square Roots",
                    "slos": [
                        {"name": "work out squares of whole numbers by multiplication in real life situations"},
                        {"name": "identify perfect squares in different situations"},
                        {"name": "work out square roots of perfect squares by factor method"},
                        {"name": "apply squares and square roots in real life situations"},
                    ],
                    "learning_experiences": "work out squares of numbers by multiplication, identify perfect squares, determine square roots using factor method, apply squares and square roots in real life",
                    "inquiry_questions": ["How do we work out squares of numbers?", "Where do we apply squares and square roots?"],
                    "core_competencies": ["Critical thinking and problem solving", "Creativity and Imagination"],
                    "values": ["Responsibility", "Unity"],
                    "pcis": ["Education for Sustainable Development"]
                },
            ]
        },
        {
            "name": "Algebra",
            "substrands": [
                {
                    "name": "Algebraic Expressions",
                    "slos": [
                        {"name": "form algebraic expressions from real life situations"},
                        {"name": "simplify algebraic expressions in different situations"},
                        {"name": "evaluate algebraic expressions by substitution in different situations"},
                        {"name": "appreciate use of algebraic expressions in real life situations"},
                    ],
                    "learning_experiences": "form algebraic expressions from word problems, simplify expressions by collecting like terms, evaluate expressions by substituting values",
                    "inquiry_questions": ["How do we form algebraic expressions?", "Where do we use algebraic expressions in real life?"],
                    "core_competencies": ["Critical thinking and problem solving", "Communication and collaboration"],
                    "values": ["Responsibility", "Respect"],
                    "pcis": ["Financial literacy"]
                },
                {
                    "name": "Linear Equations",
                    "slos": [
                        {"name": "form linear equations in one unknown from real life situations"},
                        {"name": "solve linear equations in one unknown in different situations"},
                        {"name": "apply linear equations in real life situations"},
                    ],
                    "learning_experiences": "form linear equations from word problems, solve equations using different methods, apply equations in real life contexts",
                    "inquiry_questions": ["How do we form linear equations?", "Where do we apply linear equations in daily activities?"],
                    "core_competencies": ["Critical thinking and problem solving", "Learning to learn"],
                    "values": ["Integrity", "Responsibility"],
                    "pcis": ["Financial literacy"]
                },
            ]
        },
        {
            "name": "Measurements",
            "substrands": [
                {
                    "name": "Length",
                    "slos": [
                        {"name": "convert units of length from one form to another in real life situations"},
                        {"name": "perform operations on length in real life situations"},
                        {"name": "apply length in real life situations"},
                    ],
                    "learning_experiences": "convert between different units of length, perform addition and subtraction of lengths, apply measurement of length in real life contexts",
                    "inquiry_questions": ["How do we convert units of length?", "Where do we apply measurement of length in daily activities?"],
                    "core_competencies": ["Communication and collaboration", "Critical thinking and problem solving"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Education for Sustainable Development"]
                },
                {
                    "name": "Area",
                    "slos": [
                        {"name": "calculate the area of a triangle in real life situations"},
                        {"name": "calculate the area of combined shapes involving triangles and rectangles"},
                        {"name": "apply area in real life situations"},
                    ],
                    "learning_experiences": "calculate area of triangles using formula, calculate area of combined shapes, apply area calculations in real life",
                    "inquiry_questions": ["How do we calculate the area of a triangle?", "Where do we apply area in daily activities?"],
                    "core_competencies": ["Critical thinking and problem solving", "Creativity and Imagination"],
                    "values": ["Responsibility", "Unity"],
                    "pcis": ["Education for Sustainable Development"]
                },
                {
                    "name": "Volume and Capacity",
                    "slos": [
                        {"name": "convert units of volume from one form to another in real life situations"},
                        {"name": "calculate the volume of cubes and cuboids in real life situations"},
                        {"name": "relate volume and capacity in real life situations"},
                        {"name": "apply volume and capacity in real life situations"},
                    ],
                    "learning_experiences": "convert between units of volume, calculate volume of cubes and cuboids, relate volume to capacity, apply volume and capacity in real life",
                    "inquiry_questions": ["How do we convert units of volume?", "Where do we apply volume and capacity in daily activities?"],
                    "core_competencies": ["Critical thinking and problem solving", "Learning to learn"],
                    "values": ["Integrity", "Responsibility"],
                    "pcis": ["Education for Sustainable Development"]
                },
                {
                    "name": "Mass",
                    "slos": [
                        {"name": "convert units of mass from one form to another in real life situations"},
                        {"name": "perform operations on mass in real life situations"},
                        {"name": "apply mass in real life situations"},
                    ],
                    "learning_experiences": "convert between units of mass, perform operations on mass, apply mass measurements in real life contexts",
                    "inquiry_questions": ["How do we convert units of mass?", "Where do we apply measurement of mass in daily activities?"],
                    "core_competencies": ["Communication and collaboration", "Critical thinking and problem solving"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Financial literacy"]
                },
                {
                    "name": "Time",
                    "slos": [
                        {"name": "convert units of time from one form to another in real life situations"},
                        {"name": "work out time in terms of 24-hour clock system in real life situations"},
                        {"name": "apply time in real life situations"},
                    ],
                    "learning_experiences": "convert between units of time, work with 24-hour clock system, apply time calculations in real life",
                    "inquiry_questions": ["How do we convert units of time?", "Where do we apply time in daily activities?"],
                    "core_competencies": ["Critical thinking and problem solving", "Digital literacy"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Safety and Security"]
                },
                {
                    "name": "Money",
                    "slos": [
                        {"name": "identify currencies used in Kenya and other countries"},
                        {"name": "convert currencies from one form to another in real life situations"},
                        {"name": "work out profit and loss in real life situations"},
                        {"name": "apply money in real life situations"},
                    ],
                    "learning_experiences": "identify different currencies, convert currencies, calculate profit and loss, apply money concepts in real life",
                    "inquiry_questions": ["Why do different countries have different currencies?", "How do we calculate profit and loss?"],
                    "core_competencies": ["Critical thinking and problem solving", "Citizenship"],
                    "values": ["Integrity", "Responsibility"],
                    "pcis": ["Financial literacy"]
                },
            ]
        },
        {
            "name": "Geometry",
            "substrands": [
                {
                    "name": "Lines and Angles",
                    "slos": [
                        {"name": "identify different types of lines in real life situations"},
                        {"name": "construct parallel and perpendicular lines in different situations"},
                        {"name": "identify different types of angles in real life situations"},
                        {"name": "measure and construct angles in different situations"},
                        {"name": "apply properties of angles in real life situations"},
                    ],
                    "learning_experiences": "identify and draw different types of lines, construct parallel and perpendicular lines, identify and measure angles, apply angle properties",
                    "inquiry_questions": ["How do we identify different types of lines?", "Where do we apply angles in daily activities?"],
                    "core_competencies": ["Creativity and Imagination", "Critical thinking and problem solving"],
                    "values": ["Responsibility", "Unity"],
                    "pcis": ["Education for Sustainable Development"]
                },
                {
                    "name": "Plane Figures",
                    "slos": [
                        {"name": "identify properties of triangles in different situations"},
                        {"name": "identify properties of quadrilaterals in different situations"},
                        {"name": "construct triangles and quadrilaterals in different situations"},
                        {"name": "apply properties of plane figures in real life situations"},
                    ],
                    "learning_experiences": "identify and describe properties of triangles and quadrilaterals, construct plane figures, apply properties in real life",
                    "inquiry_questions": ["How do we identify properties of plane figures?", "Where do we apply plane figures in daily activities?"],
                    "core_competencies": ["Creativity and Imagination", "Critical thinking and problem solving"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Education for Sustainable Development"]
                },
            ]
        },
        {
            "name": "Data Handling and Probability",
            "substrands": [
                {
                    "name": "Data Collection and Organization",
                    "slos": [
                        {"name": "collect data from the environment in real life situations"},
                        {"name": "organize data in frequency distribution tables in different situations"},
                        {"name": "represent data using pictographs and bar graphs in different situations"},
                        {"name": "interpret data from tables and graphs in real life situations"},
                        {"name": "apply data handling in real life situations"},
                    ],
                    "learning_experiences": "collect data from the environment, organize data in tables, represent data using pictographs and bar graphs, interpret data from graphs",
                    "inquiry_questions": ["How do we collect and organize data?", "Where do we apply data handling in daily activities?"],
                    "core_competencies": ["Communication and collaboration", "Critical thinking and problem solving", "Digital literacy"],
                    "values": ["Integrity", "Responsibility"],
                    "pcis": ["Citizenship"]
                },
                {
                    "name": "Probability",
                    "slos": [
                        {"name": "identify events in real life situations"},
                        {"name": "classify events as certain, likely, unlikely, or impossible in different situations"},
                        {"name": "apply probability concepts in real life situations"},
                    ],
                    "learning_experiences": "identify events in real life, classify events based on likelihood, apply probability concepts",
                    "inquiry_questions": ["How do we classify events?", "Where do we apply probability in daily activities?"],
                    "core_competencies": ["Critical thinking and problem solving", "Creativity and Imagination"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Safety and Security"]
                },
            ]
        },
    ]
}

# ============================================================================
# INTEGRATED SCIENCE GRADE 7 - Extracted from GRADE.7.INTEGRATED.SCIENCE.pdf
# ============================================================================
INTEGRATED_SCIENCE_GRADE_7 = {
    "name": "Integrated Science",
    "strands": [
        {
            "name": "Scientific Investigation",
            "substrands": [
                {
                    "name": "Introduction to Integrated Science",
                    "slos": [
                        {"name": "outline the components of Integrated Science as a field of study"},
                        {"name": "explain the importance of science in daily life"},
                        {"name": "show interest in learning Integrated Science at junior school"},
                    ],
                    "learning_experiences": "brainstorm on the components of Integrated Science, use digital or print media to search for information, discuss the importance of science in daily life, search for pathways related to Integrated Science at Senior School",
                    "inquiry_questions": ["How is the knowledge acquired in Integrated Science useful in daily life?"],
                    "core_competencies": ["Communication and collaboration", "Self-efficacy"],
                    "values": ["Respect", "Unity"],
                    "pcis": ["Socio-Economic Issues - cyber security"]
                },
                {
                    "name": "Laboratory Safety",
                    "slos": [
                        {"name": "identify common hazards and their symbols in the laboratory"},
                        {"name": "explain causes of common accidents in the laboratory"},
                        {"name": "demonstrate First Aid measures for common laboratory accidents"},
                        {"name": "appreciate the importance of safety in the laboratory and access to a healthy working environment"},
                    ],
                    "learning_experiences": "brainstorm on common hazards and their symbols, discuss causes of common laboratory accidents, role-play First Aid procedures, practice safety measures in the laboratory",
                    "inquiry_questions": ["How do accidents happen in the laboratory?", "What safety measures should be considered while working in the laboratory?"],
                    "core_competencies": ["Learning to learn", "Critical thinking and problem solving"],
                    "values": ["Responsibility"],
                    "pcis": ["Socio-economic issues", "Safety"]
                },
                {
                    "name": "Laboratory Apparatus and Instruments",
                    "slos": [
                        {"name": "identify basic scientific apparatus and instruments"},
                        {"name": "state the functions of basic scientific apparatus and instruments"},
                        {"name": "use basic scientific apparatus and instruments safely"},
                        {"name": "show interest in using scientific apparatus and instruments"},
                    ],
                    "learning_experiences": "identify and name laboratory apparatus, state functions of apparatus, demonstrate safe use of apparatus, practice manipulative skills",
                    "inquiry_questions": ["What are the uses of laboratory apparatus and instruments?", "Why is it important to handle apparatus carefully?"],
                    "core_competencies": ["Critical thinking and problem solving", "Learning to learn"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Safety and Security"]
                },
            ]
        },
        {
            "name": "Mixtures, Elements and Compounds",
            "substrands": [
                {
                    "name": "Classification of Substances",
                    "slos": [
                        {"name": "identify pure substances and mixtures"},
                        {"name": "classify substances as pure substances or mixtures"},
                        {"name": "distinguish between elements and compounds"},
                        {"name": "appreciate the importance of classification of substances in daily life"},
                    ],
                    "learning_experiences": "identify and classify substances, distinguish between pure substances and mixtures, distinguish between elements and compounds, appreciate classification in daily life",
                    "inquiry_questions": ["How do we classify substances?", "Why is classification of substances important?"],
                    "core_competencies": ["Critical thinking and problem solving", "Communication and collaboration"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Environmental Education"]
                },
                {
                    "name": "Mixtures and their Separation",
                    "slos": [
                        {"name": "identify types of mixtures"},
                        {"name": "describe methods of separating mixtures"},
                        {"name": "carry out separation of mixtures using different methods"},
                        {"name": "apply separation of mixtures in daily life"},
                    ],
                    "learning_experiences": "identify types of mixtures, describe separation methods, carry out separation activities, apply separation methods in daily life",
                    "inquiry_questions": ["How do we separate mixtures?", "Where do we apply separation of mixtures in daily life?"],
                    "core_competencies": ["Critical thinking and problem solving", "Creativity and Imagination"],
                    "values": ["Responsibility", "Unity"],
                    "pcis": ["Environmental Education", "Safety"]
                },
            ]
        },
        {
            "name": "Living Things and their Environment",
            "substrands": [
                {
                    "name": "Classification of Living Things",
                    "slos": [
                        {"name": "describe the characteristics of living things"},
                        {"name": "classify living things into major groups"},
                        {"name": "identify examples of organisms in each major group"},
                        {"name": "appreciate the diversity of living things"},
                    ],
                    "learning_experiences": "describe characteristics of living things, classify organisms into groups, identify examples in each group, appreciate biodiversity",
                    "inquiry_questions": ["How do we classify living things?", "Why is classification of living things important?"],
                    "core_competencies": ["Critical thinking and problem solving", "Communication and collaboration"],
                    "values": ["Respect", "Responsibility"],
                    "pcis": ["Environmental Conservation", "Biodiversity"]
                },
                {
                    "name": "The Cell",
                    "slos": [
                        {"name": "describe the structure of a cell"},
                        {"name": "identify parts of plant and animal cells"},
                        {"name": "compare plant and animal cells"},
                        {"name": "appreciate the cell as the basic unit of life"},
                    ],
                    "learning_experiences": "describe cell structure, identify cell parts using microscope, compare plant and animal cells, appreciate the importance of cells",
                    "inquiry_questions": ["What is the structure of a cell?", "Why are cells important?"],
                    "core_competencies": ["Critical thinking and problem solving", "Learning to learn"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Health Education"]
                },
                {
                    "name": "Human Body Systems",
                    "slos": [
                        {"name": "identify the digestive system and its parts"},
                        {"name": "describe the functions of parts of the digestive system"},
                        {"name": "explain the process of digestion"},
                        {"name": "appreciate the importance of maintaining a healthy digestive system"},
                    ],
                    "learning_experiences": "identify parts of digestive system, describe functions of each part, explain digestion process, discuss healthy eating habits",
                    "inquiry_questions": ["How does the digestive system work?", "How can we maintain a healthy digestive system?"],
                    "core_competencies": ["Critical thinking and problem solving", "Self-efficacy"],
                    "values": ["Responsibility"],
                    "pcis": ["Health Education", "Nutrition"]
                },
            ]
        },
        {
            "name": "Force and Energy",
            "substrands": [
                {
                    "name": "Force",
                    "slos": [
                        {"name": "define force and its effects"},
                        {"name": "identify types of forces in daily life"},
                        {"name": "measure force using a spring balance"},
                        {"name": "apply knowledge of force in daily life"},
                    ],
                    "learning_experiences": "define force, identify types of forces, measure force using spring balance, apply force concepts in daily life",
                    "inquiry_questions": ["What is force?", "How do we measure force?"],
                    "core_competencies": ["Critical thinking and problem solving", "Learning to learn"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Safety and Security"]
                },
                {
                    "name": "Pressure",
                    "slos": [
                        {"name": "define pressure"},
                        {"name": "calculate pressure in different situations"},
                        {"name": "explain factors affecting pressure"},
                        {"name": "apply knowledge of pressure in daily life"},
                    ],
                    "learning_experiences": "define pressure, calculate pressure, explain factors affecting pressure, apply pressure concepts in daily life",
                    "inquiry_questions": ["What is pressure?", "How do we calculate pressure?"],
                    "core_competencies": ["Critical thinking and problem solving", "Communication and collaboration"],
                    "values": ["Responsibility"],
                    "pcis": ["Safety and Security"]
                },
                {
                    "name": "Light",
                    "slos": [
                        {"name": "identify sources of light"},
                        {"name": "describe properties of light"},
                        {"name": "explain reflection of light"},
                        {"name": "apply knowledge of light in daily life"},
                    ],
                    "learning_experiences": "identify sources of light, describe properties of light, explain reflection, apply light concepts in daily life",
                    "inquiry_questions": ["What are the sources of light?", "How does light travel?"],
                    "core_competencies": ["Critical thinking and problem solving", "Creativity and Imagination"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Energy Conservation"]
                },
            ]
        },
    ]
}

# ============================================================================
# ENGLISH GRADE 7 - Extracted from GRADE.7.ENGLISH.pdf
# ============================================================================
ENGLISH_GRADE_7 = {
    "name": "English",
    "strands": [
        {
            "name": "Listening and Speaking",
            "substrands": [
                {
                    "name": "Conversational Skills: Polite Language",
                    "slos": [
                        {"name": "identify polite expressions used in the introduction of self and others"},
                        {"name": "use polite expressions in the introduction of self and others in different speaking contexts"},
                        {"name": "model respectful behaviour during introductions"},
                    ],
                    "learning_experiences": "make a list of necessary details about people for effective introduction, brainstorm different types of introduction, list polite expressions for introduction, role-play different contexts of self-introduction",
                    "inquiry_questions": ["Why is it important for people to introduce themselves?"],
                    "core_competencies": ["Communication and collaboration"],
                    "values": ["Respect"],
                    "pcis": ["Peace education", "Effective communication"]
                },
                {
                    "name": "Listening Comprehension",
                    "slos": [
                        {"name": "listen to a variety of texts for main ideas"},
                        {"name": "identify specific information from listening texts"},
                        {"name": "respond appropriately to questions from listening texts"},
                        {"name": "appreciate the importance of listening skills in communication"},
                    ],
                    "learning_experiences": "listen to passages and identify main ideas, pick out specific details from listening texts, answer questions based on listening passages, discuss importance of listening",
                    "inquiry_questions": ["Why is listening important in communication?", "How can we improve our listening skills?"],
                    "core_competencies": ["Communication and collaboration", "Critical thinking and problem solving"],
                    "values": ["Respect", "Responsibility"],
                    "pcis": ["Effective communication"]
                },
                {
                    "name": "Oral Narratives",
                    "slos": [
                        {"name": "identify features of oral narratives"},
                        {"name": "narrate stories using appropriate techniques"},
                        {"name": "respond to oral narratives appropriately"},
                        {"name": "appreciate the role of oral narratives in preserving culture"},
                    ],
                    "learning_experiences": "identify features of oral narratives, narrate stories with appropriate voice modulation and gestures, respond to questions about narratives, discuss cultural importance of oral narratives",
                    "inquiry_questions": ["What makes a good oral narrative?", "Why are oral narratives important in our culture?"],
                    "core_competencies": ["Communication and collaboration", "Creativity and Imagination"],
                    "values": ["Respect", "Unity"],
                    "pcis": ["Cultural heritage", "Social cohesion"]
                },
            ]
        },
        {
            "name": "Reading",
            "substrands": [
                {
                    "name": "Reading Comprehension",
                    "slos": [
                        {"name": "read a variety of texts fluently"},
                        {"name": "identify main ideas and supporting details in texts"},
                        {"name": "make inferences from texts"},
                        {"name": "appreciate the importance of reading for knowledge"},
                    ],
                    "learning_experiences": "read different types of texts, identify main ideas and supporting details, make inferences from context, discuss importance of reading",
                    "inquiry_questions": ["Why is reading important?", "How can we improve our reading skills?"],
                    "core_competencies": ["Communication and collaboration", "Critical thinking and problem solving", "Learning to learn"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Effective communication", "Lifelong learning"]
                },
                {
                    "name": "Vocabulary Development",
                    "slos": [
                        {"name": "use context clues to determine meaning of unfamiliar words"},
                        {"name": "use dictionaries to find meanings of words"},
                        {"name": "use new vocabulary in sentences"},
                        {"name": "appreciate the importance of expanding vocabulary"},
                    ],
                    "learning_experiences": "use context to determine word meanings, use dictionaries and thesauruses, form sentences using new vocabulary, discuss importance of vocabulary",
                    "inquiry_questions": ["How do we learn new words?", "Why is vocabulary important?"],
                    "core_competencies": ["Communication and collaboration", "Learning to learn"],
                    "values": ["Responsibility"],
                    "pcis": ["Effective communication"]
                },
                {
                    "name": "Literary Appreciation",
                    "slos": [
                        {"name": "identify literary devices in texts"},
                        {"name": "analyse characters, themes and settings in literary texts"},
                        {"name": "relate literary texts to real life experiences"},
                        {"name": "appreciate the role of literature in society"},
                    ],
                    "learning_experiences": "identify literary devices like similes and metaphors, analyse characters and themes, relate stories to real life, discuss role of literature",
                    "inquiry_questions": ["What are literary devices?", "Why is literature important?"],
                    "core_competencies": ["Critical thinking and problem solving", "Creativity and Imagination"],
                    "values": ["Respect", "Unity"],
                    "pcis": ["Cultural heritage", "Social cohesion"]
                },
            ]
        },
        {
            "name": "Grammar in Use",
            "substrands": [
                {
                    "name": "Parts of Speech",
                    "slos": [
                        {"name": "identify different parts of speech in sentences"},
                        {"name": "use nouns, verbs, adjectives and adverbs correctly"},
                        {"name": "construct sentences using different parts of speech"},
                        {"name": "appreciate the importance of grammar in communication"},
                    ],
                    "learning_experiences": "identify parts of speech in sentences, use nouns verbs adjectives and adverbs correctly, construct sentences, discuss importance of grammar",
                    "inquiry_questions": ["What are the parts of speech?", "Why is grammar important?"],
                    "core_competencies": ["Communication and collaboration", "Learning to learn"],
                    "values": ["Responsibility"],
                    "pcis": ["Effective communication"]
                },
                {
                    "name": "Sentence Structure",
                    "slos": [
                        {"name": "identify different types of sentences"},
                        {"name": "construct simple, compound and complex sentences"},
                        {"name": "use correct punctuation in sentences"},
                        {"name": "appreciate the importance of correct sentence structure"},
                    ],
                    "learning_experiences": "identify types of sentences, construct different sentence types, use punctuation correctly, discuss importance of sentence structure",
                    "inquiry_questions": ["What are the different types of sentences?", "Why is punctuation important?"],
                    "core_competencies": ["Communication and collaboration", "Critical thinking and problem solving"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Effective communication"]
                },
                {
                    "name": "Tenses",
                    "slos": [
                        {"name": "identify different tenses in sentences"},
                        {"name": "use present, past and future tenses correctly"},
                        {"name": "construct sentences in different tenses"},
                        {"name": "appreciate the importance of using correct tenses"},
                    ],
                    "learning_experiences": "identify tenses in sentences, use different tenses correctly, construct sentences in various tenses, discuss importance of tenses",
                    "inquiry_questions": ["What are the different tenses?", "Why is it important to use correct tenses?"],
                    "core_competencies": ["Communication and collaboration", "Learning to learn"],
                    "values": ["Responsibility"],
                    "pcis": ["Effective communication"]
                },
            ]
        },
        {
            "name": "Writing",
            "substrands": [
                {
                    "name": "Creative Writing",
                    "slos": [
                        {"name": "write creative compositions on given topics"},
                        {"name": "use descriptive language in writing"},
                        {"name": "organize ideas logically in writing"},
                        {"name": "appreciate the importance of creative writing"},
                    ],
                    "learning_experiences": "write compositions on various topics, use descriptive language, organize ideas logically, discuss importance of creative writing",
                    "inquiry_questions": ["What makes good creative writing?", "Why is creative writing important?"],
                    "core_competencies": ["Communication and collaboration", "Creativity and Imagination"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Effective communication", "Creativity"]
                },
                {
                    "name": "Functional Writing",
                    "slos": [
                        {"name": "write different types of functional texts"},
                        {"name": "use appropriate format for different functional texts"},
                        {"name": "convey information clearly in functional writing"},
                        {"name": "appreciate the importance of functional writing in daily life"},
                    ],
                    "learning_experiences": "write letters notices and reports, use appropriate formats, convey information clearly, discuss importance of functional writing",
                    "inquiry_questions": ["What are the different types of functional writing?", "Why is functional writing important?"],
                    "core_competencies": ["Communication and collaboration", "Critical thinking and problem solving"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": ["Effective communication", "Lifelong learning"]
                },
            ]
        },
    ]
}

# ============================================================================
# KISWAHILI GRADE 7 - Extracted from Kiswahili-Grade-7-.pdf
# ============================================================================
KISWAHILI_GRADE_7 = {
    "name": "Kiswahili",
    "strands": [
        {
            "name": "Kusikiliza na Kuzungumza",
            "substrands": [
                {
                    "name": "Mazungumzo",
                    "slos": [
                        {"name": "kutambua mada za mazungumzo mbalimbali"},
                        {"name": "kushiriki mazungumzo kuhusu mada mbalimbali"},
                        {"name": "kuzingatia adabu za mazungumzo"},
                        {"name": "kuthamini umuhimu wa mazungumzo katika mawasiliano"},
                    ],
                    "learning_experiences": "kutambua mada za mazungumzo, kushiriki mazungumzo, kuzingatia adabu, kuthamini mazungumzo",
                    "inquiry_questions": ["Mazungumzo yana umuhimu gani?", "Adabu gani zinazofaa kuzingatiwa wakati wa mazungumzo?"],
                    "core_competencies": ["Mawasiliano na ushirikiano", "Kujiamini"],
                    "values": ["Heshima", "Upendo"],
                    "pcis": ["Mawasiliano bora"]
                },
                {
                    "name": "Kusikiliza kwa Ufahamu",
                    "slos": [
                        {"name": "kusikiliza vifungu mbalimbali kwa umakini"},
                        {"name": "kutambua ujumbe katika vifungu"},
                        {"name": "kujibu maswali kuhusu vifungu vilivyosomwa"},
                        {"name": "kuthamini umuhimu wa kusikiliza kwa ufahamu"},
                    ],
                    "learning_experiences": "kusikiliza vifungu mbalimbali, kutambua ujumbe, kujibu maswali, kuthamini kusikiliza",
                    "inquiry_questions": ["Kusikiliza kwa ufahamu kuna umuhimu gani?"],
                    "core_competencies": ["Mawasiliano na ushirikiano", "Fikra makini"],
                    "values": ["Heshima", "Uwajibikaji"],
                    "pcis": ["Mawasiliano bora"]
                },
            ]
        },
        {
            "name": "Kusoma",
            "substrands": [
                {
                    "name": "Kusoma kwa Ufahamu",
                    "slos": [
                        {"name": "kusoma vifungu mbalimbali kwa ufasaha"},
                        {"name": "kutambua maana ya maneno kutokana na muktadha"},
                        {"name": "kujibu maswali kuhusu vifungu vilivyosomwa"},
                        {"name": "kuthamini umuhimu wa kusoma katika maisha"},
                    ],
                    "learning_experiences": "kusoma vifungu mbalimbali, kutambua maana ya maneno, kujibu maswali, kuthamini kusoma",
                    "inquiry_questions": ["Kusoma kuna umuhimu gani katika maisha?"],
                    "core_competencies": ["Mawasiliano na ushirikiano", "Kujifunza kujifunza"],
                    "values": ["Uwajibikaji", "Uadilifu"],
                    "pcis": ["Elimu ya kudumu"]
                },
                {
                    "name": "Fasihi Simulizi",
                    "slos": [
                        {"name": "kutambua aina za fasihi simulizi"},
                        {"name": "kueleza sifa za hadithi na ngano"},
                        {"name": "kusimulia hadithi kwa mbinu zinazofaa"},
                        {"name": "kuthamini umuhimu wa fasihi simulizi katika utamaduni"},
                    ],
                    "learning_experiences": "kutambua aina za fasihi simulizi, kueleza sifa za hadithi, kusimulia hadithi, kuthamini fasihi simulizi",
                    "inquiry_questions": ["Fasihi simulizi ina umuhimu gani?"],
                    "core_competencies": ["Mawasiliano na ushirikiano", "Ubunifu"],
                    "values": ["Heshima", "Umoja"],
                    "pcis": ["Urithi wa kitamaduni"]
                },
            ]
        },
        {
            "name": "Kuandika",
            "substrands": [
                {
                    "name": "Insha za Ubunifu",
                    "slos": [
                        {"name": "kuandika insha za ubunifu kuhusu mada mbalimbali"},
                        {"name": "kutumia lugha ya kitamathali katika kuandika"},
                        {"name": "kupanga mawazo kwa mantiki katika kuandika"},
                        {"name": "kuthamini umuhimu wa kuandika kwa ubunifu"},
                    ],
                    "learning_experiences": "kuandika insha za ubunifu, kutumia lugha ya kitamathali, kupanga mawazo, kuthamini kuandika",
                    "inquiry_questions": ["Kuandika kwa ubunifu kuna umuhimu gani?"],
                    "core_competencies": ["Mawasiliano na ushirikiano", "Ubunifu"],
                    "values": ["Uwajibikaji", "Uadilifu"],
                    "pcis": ["Ubunifu"]
                },
                {
                    "name": "Barua",
                    "slos": [
                        {"name": "kutambua aina za barua"},
                        {"name": "kuandika barua rasmi na zisizo rasmi"},
                        {"name": "kutumia muundo unaofaa wa barua"},
                        {"name": "kuthamini umuhimu wa kuandika barua"},
                    ],
                    "learning_experiences": "kutambua aina za barua, kuandika barua mbalimbali, kutumia muundo unaofaa, kuthamini barua",
                    "inquiry_questions": ["Barua zina umuhimu gani katika mawasiliano?"],
                    "core_competencies": ["Mawasiliano na ushirikiano", "Fikra makini"],
                    "values": ["Uwajibikaji"],
                    "pcis": ["Mawasiliano bora"]
                },
            ]
        },
        {
            "name": "Sarufi",
            "substrands": [
                {
                    "name": "Ngeli za Nomino",
                    "slos": [
                        {"name": "kutambua ngeli mbalimbali za nomino"},
                        {"name": "kuweka nomino katika ngeli zake"},
                        {"name": "kutumia nomino za ngeli mbalimbali katika sentensi"},
                        {"name": "kuthamini umuhimu wa ngeli katika lugha ya Kiswahili"},
                    ],
                    "learning_experiences": "kutambua ngeli za nomino, kuweka nomino katika ngeli, kutumia nomino katika sentensi, kuthamini ngeli",
                    "inquiry_questions": ["Ngeli za nomino zina umuhimu gani?"],
                    "core_competencies": ["Mawasiliano na ushirikiano", "Kujifunza kujifunza"],
                    "values": ["Uwajibikaji"],
                    "pcis": ["Mawasiliano bora"]
                },
                {
                    "name": "Vitenzi",
                    "slos": [
                        {"name": "kutambua aina za vitenzi"},
                        {"name": "kutumia vitenzi katika nyakati mbalimbali"},
                        {"name": "kuunda sentensi kwa kutumia vitenzi"},
                        {"name": "kuthamini matumizi sahihi ya vitenzi"},
                    ],
                    "learning_experiences": "kutambua aina za vitenzi, kutumia vitenzi katika nyakati mbalimbali, kuunda sentensi, kuthamini vitenzi",
                    "inquiry_questions": ["Vitenzi vina umuhimu gani katika sentensi?"],
                    "core_competencies": ["Mawasiliano na ushirikiano", "Fikra makini"],
                    "values": ["Uwajibikaji", "Uadilifu"],
                    "pcis": ["Mawasiliano bora"]
                },
            ]
        },
    ]
}

# ============================================================================
# SOCIAL STUDIES GRADE 7 - Extracted from Social-Studies-Grade-7-Formatted-April-2024.pdf
# ============================================================================
SOCIAL_STUDIES_GRADE_7 = {
    "name": "Social Studies",
    "strands": [
        {
            "name": "Social Studies and Career Development",
            "substrands": [
                {
                    "name": "Career Awareness",
                    "slos": [
                        {"name": "identify different careers in the society"},
                        {"name": "explain factors that influence career choice"},
                        {"name": "relate school subjects to different careers"},
                        {"name": "appreciate the importance of career awareness"},
                    ],
                    "learning_experiences": "identify different careers, discuss factors influencing career choice, relate subjects to careers, appreciate career awareness",
                    "inquiry_questions": ["What factors influence career choice?", "How do school subjects relate to careers?"],
                    "core_competencies": ["Self-efficacy", "Learning to learn"],
                    "values": ["Responsibility"],
                    "pcis": ["Career guidance"]
                },
            ]
        },
        {
            "name": "Community Service-Learning",
            "substrands": [
                {
                    "name": "Community Service-Learning Project",
                    "slos": [
                        {"name": "identify community needs in the locality"},
                        {"name": "plan community service activities"},
                        {"name": "participate in community service activities"},
                        {"name": "appreciate the importance of community service"},
                    ],
                    "learning_experiences": "identify community needs, plan service activities, participate in community service, appreciate community service",
                    "inquiry_questions": ["What are the needs in our community?", "How can we serve our community?"],
                    "core_competencies": ["Citizenship", "Communication and collaboration"],
                    "values": ["Responsibility", "Unity"],
                    "pcis": ["Citizenship", "Social cohesion"]
                },
            ]
        },
        {
            "name": "People and Relationships",
            "substrands": [
                {
                    "name": "The Family",
                    "slos": [
                        {"name": "describe types of families in the society"},
                        {"name": "explain roles and responsibilities of family members"},
                        {"name": "identify challenges facing families in the society"},
                        {"name": "appreciate the importance of family in the society"},
                    ],
                    "learning_experiences": "describe types of families, explain roles of family members, identify family challenges, appreciate family importance",
                    "inquiry_questions": ["What are the types of families?", "What roles do family members play?"],
                    "core_competencies": ["Communication and collaboration", "Self-efficacy"],
                    "values": ["Responsibility", "Love", "Unity"],
                    "pcis": ["Family life education"]
                },
                {
                    "name": "Population",
                    "slos": [
                        {"name": "describe the distribution of population in Kenya"},
                        {"name": "explain factors influencing population distribution"},
                        {"name": "identify effects of population growth"},
                        {"name": "appreciate the importance of population studies"},
                    ],
                    "learning_experiences": "describe population distribution, explain factors influencing distribution, identify effects of population growth, appreciate population studies",
                    "inquiry_questions": ["What factors influence population distribution?", "What are the effects of population growth?"],
                    "core_competencies": ["Critical thinking and problem solving", "Communication and collaboration"],
                    "values": ["Responsibility", "Patriotism"],
                    "pcis": ["Population education"]
                },
            ]
        },
        {
            "name": "Natural and Historic Built Environments",
            "substrands": [
                {
                    "name": "Physical Features",
                    "slos": [
                        {"name": "identify physical features in Kenya"},
                        {"name": "describe the formation of physical features"},
                        {"name": "explain the importance of physical features"},
                        {"name": "appreciate the need to conserve physical features"},
                    ],
                    "learning_experiences": "identify physical features, describe formation of features, explain importance of features, appreciate conservation",
                    "inquiry_questions": ["How are physical features formed?", "Why should we conserve physical features?"],
                    "core_competencies": ["Critical thinking and problem solving", "Learning to learn"],
                    "values": ["Responsibility", "Patriotism"],
                    "pcis": ["Environmental conservation"]
                },
                {
                    "name": "Climate and Weather",
                    "slos": [
                        {"name": "differentiate between weather and climate"},
                        {"name": "describe elements of weather"},
                        {"name": "explain factors influencing climate in Kenya"},
                        {"name": "appreciate the importance of weather and climate"},
                    ],
                    "learning_experiences": "differentiate weather and climate, describe weather elements, explain factors influencing climate, appreciate weather and climate",
                    "inquiry_questions": ["What is the difference between weather and climate?", "What factors influence climate?"],
                    "core_competencies": ["Critical thinking and problem solving", "Communication and collaboration"],
                    "values": ["Responsibility"],
                    "pcis": ["Climate change education"]
                },
            ]
        },
        {
            "name": "Political Developments and Governance",
            "substrands": [
                {
                    "name": "Government",
                    "slos": [
                        {"name": "describe the structure of the government in Kenya"},
                        {"name": "explain the functions of the three arms of government"},
                        {"name": "identify the role of citizens in governance"},
                        {"name": "appreciate the importance of good governance"},
                    ],
                    "learning_experiences": "describe government structure, explain functions of arms of government, identify role of citizens, appreciate good governance",
                    "inquiry_questions": ["What are the functions of the government?", "What is the role of citizens in governance?"],
                    "core_competencies": ["Citizenship", "Critical thinking and problem solving"],
                    "values": ["Patriotism", "Responsibility", "Integrity"],
                    "pcis": ["Citizenship education", "Good governance"]
                },
                {
                    "name": "Democracy and Human Rights",
                    "slos": [
                        {"name": "explain the meaning of democracy"},
                        {"name": "identify human rights and responsibilities"},
                        {"name": "explain the importance of democracy and human rights"},
                        {"name": "appreciate the need to promote democracy and human rights"},
                    ],
                    "learning_experiences": "explain democracy, identify human rights and responsibilities, explain importance of democracy, appreciate democracy and human rights",
                    "inquiry_questions": ["What is democracy?", "Why are human rights important?"],
                    "core_competencies": ["Citizenship", "Communication and collaboration"],
                    "values": ["Respect", "Responsibility", "Social Justice"],
                    "pcis": ["Human rights education", "Citizenship education"]
                },
            ]
        },
    ]
}

# All Grade 7 subjects
ALL_GRADE_7_SUBJECTS = [
    MATHEMATICS_GRADE_7,
    INTEGRATED_SCIENCE_GRADE_7,
    ENGLISH_GRADE_7,
    KISWAHILI_GRADE_7,
    SOCIAL_STUDIES_GRADE_7,
]


async def get_or_create_grade(grade_name):
    """Get or create a grade."""
    grade = await db.grades.find_one({"name": grade_name})
    if not grade:
        result = await db.grades.insert_one({"name": grade_name})
        return str(result.inserted_id)
    return str(grade["_id"])


async def find_subject_by_name(subject_name):
    """Find a subject by name."""
    return await db.subjects.find_one({"name": subject_name})


async def ensure_subject_has_grade(subject_id, grade_id):
    """Ensure a subject has a grade in its gradeIds array."""
    subject = await db.subjects.find_one({"_id": ObjectId(subject_id)})
    if subject:
        current_grade_ids = subject.get("gradeIds", [])
        if grade_id not in current_grade_ids:
            current_grade_ids.append(grade_id)
            await db.subjects.update_one(
                {"_id": ObjectId(subject_id)},
                {"$set": {"gradeIds": current_grade_ids}}
            )
            print(f"  Added Grade 7 to subject")


async def delete_existing_strands_for_subject(subject_id):
    """Delete existing strands and all related data for a subject."""
    strands = await db.strands.find({"subjectId": subject_id}).to_list(1000)
    
    for strand in strands:
        strand_id = str(strand["_id"])
        substrands = await db.substrands.find({"strandId": strand_id}).to_list(1000)
        
        for substrand in substrands:
            substrand_id = str(substrand["_id"])
            slos = await db.slos.find({"substrandId": substrand_id}).to_list(1000)
            
            for slo in slos:
                slo_id = str(slo["_id"])
                # Delete SLO mappings
                await db.slo_mappings.delete_many({"sloId": slo_id})
                # Delete learning activities
                await db.learning_activities.delete_many({"sloId": slo_id})
            
            # Delete SLOs
            await db.slos.delete_many({"substrandId": substrand_id})
        
        # Delete substrands
        await db.substrands.delete_many({"strandId": strand_id})
    
    # Delete strands
    deleted = await db.strands.delete_many({"subjectId": subject_id})
    return deleted.deleted_count


async def get_competency_ids(competency_names):
    """Get competency IDs from names, creating if needed."""
    ids = []
    for name in competency_names:
        comp = await db.competencies.find_one({"name": name})
        if comp:
            ids.append(str(comp["_id"]))
    return ids


async def get_value_ids(value_names):
    """Get value IDs from names."""
    ids = []
    for name in value_names:
        val = await db.values.find_one({"name": name})
        if val:
            ids.append(str(val["_id"]))
    return ids


async def get_pci_ids(pci_names):
    """Get PCI IDs from names."""
    ids = []
    for name in pci_names:
        pci = await db.pcis.find_one({"name": name})
        if pci:
            ids.append(str(pci["_id"]))
    return ids


async def seed_subject(subject_data, grade_id):
    """Seed curriculum data for a single subject."""
    subject_name = subject_data["name"]
    print(f"\n{'='*60}")
    print(f"Processing: {subject_name}")
    print(f"{'='*60}")
    
    # Find existing subject
    subject = await find_subject_by_name(subject_name)
    
    if not subject:
        print(f"  WARNING: Subject '{subject_name}' not found. Creating...")
        result = await db.subjects.insert_one({
            "name": subject_name,
            "gradeIds": [grade_id]
        })
        subject_id = str(result.inserted_id)
    else:
        subject_id = str(subject["_id"])
        print(f"  Found subject ID: {subject_id}")
        await ensure_subject_has_grade(subject_id, grade_id)
    
    # Delete existing data for this subject
    deleted = await delete_existing_strands_for_subject(subject_id)
    print(f"  Deleted {deleted} existing strands")
    
    strand_count = 0
    substrand_count = 0
    slo_count = 0
    mapping_count = 0
    
    # Create strands in order
    for strand_data in subject_data["strands"]:
        strand_result = await db.strands.insert_one({
            "name": strand_data["name"],
            "subjectId": subject_id,
            "createdAt": datetime.utcnow()
        })
        strand_id = str(strand_result.inserted_id)
        strand_count += 1
        print(f"  Created Strand: {strand_data['name']}")
        
        # Create substrands in order
        for substrand_data in strand_data["substrands"]:
            substrand_result = await db.substrands.insert_one({
                "name": substrand_data["name"],
                "strandId": strand_id,
                "createdAt": datetime.utcnow()
            })
            substrand_id = str(substrand_result.inserted_id)
            substrand_count += 1
            
            # Get competency, value, and PCI IDs
            competency_ids = await get_competency_ids(substrand_data.get("core_competencies", []))
            value_ids = await get_value_ids(substrand_data.get("values", []))
            pci_ids = await get_pci_ids(substrand_data.get("pcis", []))
            
            # Create SLOs in order
            for slo_data in substrand_data["slos"]:
                slo_result = await db.slos.insert_one({
                    "name": slo_data["name"],
                    "description": slo_data.get("description", ""),
                    "substrandId": substrand_id,
                    "createdAt": datetime.utcnow()
                })
                slo_id = str(slo_result.inserted_id)
                slo_count += 1
                
                # Create SLO mapping
                await db.slo_mappings.insert_one({
                    "sloId": slo_id,
                    "competencyIds": competency_ids,
                    "valueIds": value_ids,
                    "pciIds": pci_ids,
                    "assessmentIds": []
                })
                mapping_count += 1
            
            # Create learning activity for this substrand
            await db.learning_activities.insert_one({
                "substrandId": substrand_id,
                "introduction_activities": substrand_data.get("learning_experiences", "").split(", ")[:3],
                "development_activities": substrand_data.get("learning_experiences", "").split(", ")[3:6],
                "conclusion_activities": substrand_data.get("learning_experiences", "").split(", ")[6:],
                "createdAt": datetime.utcnow()
            })
    
    print(f"\n  Summary for {subject_name}:")
    print(f"    - Strands: {strand_count}")
    print(f"    - Substrands: {substrand_count}")
    print(f"    - SLOs: {slo_count}")
    print(f"    - SLO Mappings: {mapping_count}")
    
    return strand_count, substrand_count, slo_count, mapping_count


async def main():
    """Main function to seed Grade 7 curriculum data."""
    print("\n" + "="*70)
    print("GRADE 7 COMPLETE CURRICULUM SEEDING")
    print("Data extracted from official KICD PDFs")
    print("="*70)
    
    # Get or create Grade 7
    grade_id = await get_or_create_grade("Grade 7")
    print(f"\nGrade 7 ID: {grade_id}")
    
    total_strands = 0
    total_substrands = 0
    total_slos = 0
    total_mappings = 0
    
    # Seed each subject
    for subject_data in ALL_GRADE_7_SUBJECTS:
        strands, substrands, slos, mappings = await seed_subject(subject_data, grade_id)
        total_strands += strands
        total_substrands += substrands
        total_slos += slos
        total_mappings += mappings
    
    print("\n" + "="*70)
    print("SEEDING COMPLETE!")
    print("="*70)
    print(f"\nTotal Statistics:")
    print(f"  - Strands: {total_strands}")
    print(f"  - Substrands: {total_substrands}")
    print(f"  - SLOs: {total_slos}")
    print(f"  - SLO Mappings: {total_mappings}")


if __name__ == "__main__":
    asyncio.run(main())
