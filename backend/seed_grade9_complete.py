#!/usr/bin/env python3
"""
Seed Grade 9 KICD Curriculum Design PDFs.
Links to EXISTING subjects - does not create duplicates.
Extracts complete data: Strands, Substrands, SLOs, Learning Experiences,
Inquiry Questions, Core Competencies, Values, PCIs.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

mongo_url = os.environ.get('MONGO_URL') or os.environ.get('MONGODB_URI')
db_name = os.environ.get('DB_NAME', 'cbeplanner')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]


# ============================================================================
# MATHEMATICS GRADE 9 - Complete Curriculum Data
# ============================================================================
MATHEMATICS_GRADE_9 = {
    "name": "Mathematics",
    "strands": [
        {
            "name": "Numbers",
            "substrands": [
                {
                    "name": "Integers",
                    "slos": [
                        {"name": "Work out combined operations of integers", "description": "By the end of the sub-strand the learner should be able to work out combined operations of integers in the correct order in different situations."},
                        {"name": "Read and record temperature changes", "description": "By the end of the sub-strand the learner should be able to read and record temperature changes on a thermometer in real life situations."},
                        {"name": "Use IT devices to determine temperature", "description": "By the end of the sub-strand the learner should be able to use IT devices to determine temperature in different situations."},
                    ],
                    "learning_experiences": [
                        "Work out combined operations of integers in the correct order",
                        "Read temperature changes in a thermometer and discuss how to record it",
                        "Use IT devices to determine temperature"
                    ],
                    "inquiry_questions": ["How do we work out combined operations of integers?", "Where do we apply integers in real life?"],
                    "core_competencies": ["Critical thinking and problem solving - interpretation and inference", "Learning to learn - organizing own learning", "Digital literacy - interacting with technologies"],
                    "values": ["Respect - working in pairs/groups", "Unity - working towards achieving set goals"],
                    "pcis": ["Environmental education - reading temperature changes that tell about climate"]
                },
                {
                    "name": "Cubes and Cube Roots",
                    "slos": [
                        {"name": "Work out cubes of numbers by multiplication", "description": "By the end of the sub-strand the learner should be able to work out cubes of numbers by multiplication in real life situations."},
                        {"name": "Determine cubes from mathematical tables", "description": "By the end of the sub-strand the learner should be able to determine cubes of numbers from mathematical tables in different situations."},
                        {"name": "Determine cube roots by factor method", "description": "By the end of the sub-strand the learner should be able to determine cube roots of numbers by factor method in different situations."},
                        {"name": "Determine cube roots from tables", "description": "By the end of the sub-strand the learner should be able to determine cube roots of numbers from mathematical tables in different situations."},
                        {"name": "Apply cubes and cube roots in real life", "description": "By the end of the sub-strand the learner should be able to apply cubes and cube roots in real life situations."},
                        {"name": "Work out cubes and cube roots using IT", "description": "By the end of the sub-strand the learner should be able to work out cubes and cube roots using IT devices."},
                    ],
                    "learning_experiences": [
                        "Use stacks of cubes to demonstrate the concept of cube and cube roots",
                        "Demonstrate stacking of cubes",
                        "Discuss the volume of a cube and determine both the cube and cube root",
                        "Read the cube of numbers from mathematical tables and relate to cube roots",
                        "Use IT devices to determine cube and cube roots of numbers"
                    ],
                    "inquiry_questions": ["How do we work out the cubes of numbers?", "How do we work out the cube roots of numbers?", "Where do we apply cubes and cube roots in real life?"],
                    "core_competencies": ["Communication and collaboration - speaking and listening", "Imagination and creativity - open mindedness"],
                    "values": ["Respect - appreciating each other's contribution"],
                    "pcis": []
                },
                {
                    "name": "Compound Proportions and Rates of Work",
                    "slos": [
                        {"name": "Divide quantities into proportional parts", "description": "By the end of the sub-strand the learner should be able to divide quantities into proportional parts in real life situations."},
                        {"name": "Relate different ratios", "description": "By the end of the sub-strand the learner should be able to relate different ratios in real life situations."},
                        {"name": "Work out compound proportions using ratio method", "description": "By the end of the sub-strand the learner should be able to work out compound proportions using ratio method in different situations."},
                        {"name": "Calculate rates of work", "description": "By the end of the sub-strand the learner should be able to calculate rates of work in real life situations."},
                        {"name": "Apply compound proportions in real life", "description": "By the end of the sub-strand the learner should be able to appreciate use of compound proportions and rates of work in real life situations."},
                    ],
                    "learning_experiences": [
                        "Discuss and divide quantities into proportional parts and express as a fraction",
                        "Compare and write different ratios",
                        "Determine compound proportions using ratios",
                        "Work out rates of work",
                        "Play games on rates of work using IT devices"
                    ],
                    "inquiry_questions": ["What are proportions?", "Why do we work fast?"],
                    "core_competencies": ["Citizenship - active community life skills", "Critical thinking and problem solving - interpretation and inference"],
                    "values": ["Responsibility - committing to working out answers", "Respect for self and others"],
                    "pcis": ["Self-esteem - devising personal strategies"]
                },
            ]
        },
        {
            "name": "Algebra",
            "substrands": [
                {
                    "name": "Indices and Logarithms",
                    "slos": [
                        {"name": "Express numbers in index form", "description": "By the end of the sub-strand the learner should be able to express numbers in index form in different situations."},
                        {"name": "Generate the laws of indices", "description": "By the end of the sub-strand the learner should be able to generate the laws of indices in different situations."},
                        {"name": "Apply the laws of indices", "description": "By the end of the sub-strand the learner should be able to apply the laws of indices in different situations."},
                        {"name": "Relate powers of 10 to common logarithms", "description": "By the end of the sub-strand the learner should be able to relate powers of 10 to common logarithms in different situations."},
                        {"name": "Use IT for indices and logarithms", "description": "By the end of the sub-strand the learner should be able to use IT to learn more on indices and common logarithms."},
                    ],
                    "learning_experiences": [
                        "Discuss indices and identify the base",
                        "Show the laws of indices using multiplication and division",
                        "Use the laws of indices to work out indices",
                        "Discuss and relate powers of 10 to common logarithms",
                        "Use IT to work out common logarithms or use mathematical tables"
                    ],
                    "inquiry_questions": ["How do we express numbers in powers?"],
                    "core_competencies": ["Critical thinking and problem solving", "Self-efficacy"],
                    "values": ["Responsibility - taking roles in turns to lead discussions", "Unity"],
                    "pcis": ["Self-awareness"]
                },
                {
                    "name": "Matrices",
                    "slos": [
                        {"name": "Identify and represent a matrix", "description": "By the end of the sub-strand the learner should be able to identify and represent a matrix in different situations."},
                        {"name": "Determine the order of a matrix", "description": "By the end of the sub-strand the learner should be able to determine the order of a matrix in different situations."},
                        {"name": "Add and subtract matrices", "description": "By the end of the sub-strand the learner should be able to add and subtract matrices in different situations."},
                        {"name": "Multiply a matrix by a scalar", "description": "By the end of the sub-strand the learner should be able to multiply a matrix by a scalar in different situations."},
                        {"name": "Apply matrices in real life", "description": "By the end of the sub-strand the learner should be able to apply matrices in real life situations."},
                    ],
                    "learning_experiences": [
                        "Discuss the concept of a matrix and identify entries",
                        "Determine the order of a matrix",
                        "Perform addition and subtraction of matrices",
                        "Multiply a matrix by a scalar",
                        "Apply matrices in organizing data and solving problems"
                    ],
                    "inquiry_questions": ["What is a matrix?", "Where do we use matrices in real life?"],
                    "core_competencies": ["Critical thinking and problem solving", "Communication and collaboration"],
                    "values": ["Responsibility", "Unity"],
                    "pcis": []
                },
                {
                    "name": "Quadratic Expressions and Equations",
                    "slos": [
                        {"name": "Expand quadratic expressions", "description": "By the end of the sub-strand the learner should be able to expand quadratic expressions in different situations."},
                        {"name": "Factorize quadratic expressions", "description": "By the end of the sub-strand the learner should be able to factorize quadratic expressions in different situations."},
                        {"name": "Form quadratic equations", "description": "By the end of the sub-strand the learner should be able to form quadratic equations from real life situations."},
                        {"name": "Solve quadratic equations by factorization", "description": "By the end of the sub-strand the learner should be able to solve quadratic equations by factorization method."},
                    ],
                    "learning_experiences": [
                        "Expand quadratic expressions using FOIL method",
                        "Factorize quadratic expressions",
                        "Form quadratic equations from word problems",
                        "Solve quadratic equations by factorization",
                        "Apply quadratic equations to solve real life problems"
                    ],
                    "inquiry_questions": ["How do we expand quadratic expressions?", "How do we solve quadratic equations?"],
                    "core_competencies": ["Critical thinking and problem solving", "Learning to learn"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": []
                },
                {
                    "name": "Linear Inequalities",
                    "slos": [
                        {"name": "Solve linear inequalities in one unknown", "description": "By the end of the sub-strand the learner should be able to solve linear inequalities in one unknown."},
                        {"name": "Represent solutions on a number line", "description": "By the end of the sub-strand the learner should be able to represent solutions of inequalities on a number line."},
                        {"name": "Solve simultaneous inequalities", "description": "By the end of the sub-strand the learner should be able to solve simultaneous linear inequalities."},
                        {"name": "Apply inequalities in real life", "description": "By the end of the sub-strand the learner should be able to apply linear inequalities in real life situations."},
                    ],
                    "learning_experiences": [
                        "Solve linear inequalities in one unknown",
                        "Represent solutions on a number line",
                        "Solve pairs of simultaneous inequalities",
                        "Apply inequalities to solve real life problems"
                    ],
                    "inquiry_questions": ["How do we solve linear inequalities?", "Where do we apply inequalities?"],
                    "core_competencies": ["Critical thinking and problem solving", "Learning to learn"],
                    "values": ["Responsibility"],
                    "pcis": []
                },
            ]
        },
        {
            "name": "Measurements",
            "substrands": [
                {
                    "name": "Pythagoras Theorem",
                    "slos": [
                        {"name": "State Pythagoras theorem", "description": "By the end of the sub-strand the learner should be able to state Pythagoras theorem."},
                        {"name": "Apply Pythagoras theorem", "description": "By the end of the sub-strand the learner should be able to apply Pythagoras theorem to calculate sides of right-angled triangles."},
                        {"name": "Solve problems using Pythagoras theorem", "description": "By the end of the sub-strand the learner should be able to solve real life problems using Pythagoras theorem."},
                    ],
                    "learning_experiences": [
                        "Discover Pythagoras theorem through practical activities",
                        "State the relationship a² + b² = c²",
                        "Calculate sides of right-angled triangles",
                        "Solve real life problems involving Pythagoras theorem"
                    ],
                    "inquiry_questions": ["What is Pythagoras theorem?", "Where do we apply Pythagoras theorem?"],
                    "core_competencies": ["Critical thinking and problem solving", "Learning to learn"],
                    "values": ["Responsibility"],
                    "pcis": []
                },
                {
                    "name": "Trigonometric Ratios",
                    "slos": [
                        {"name": "Identify trigonometric ratios", "description": "By the end of the sub-strand the learner should be able to identify sine, cosine and tangent ratios in right-angled triangles."},
                        {"name": "Calculate trigonometric ratios", "description": "By the end of the sub-strand the learner should be able to calculate trigonometric ratios of given angles."},
                        {"name": "Use trigonometric tables", "description": "By the end of the sub-strand the learner should be able to use trigonometric tables to find ratios."},
                        {"name": "Apply trigonometry in real life", "description": "By the end of the sub-strand the learner should be able to apply trigonometry in solving real life problems."},
                    ],
                    "learning_experiences": [
                        "Define sine, cosine and tangent ratios",
                        "Calculate trigonometric ratios from right-angled triangles",
                        "Use trigonometric tables to find values",
                        "Apply trigonometry to calculate heights and distances"
                    ],
                    "inquiry_questions": ["What are trigonometric ratios?", "How do we apply trigonometry?"],
                    "core_competencies": ["Critical thinking and problem solving", "Digital literacy"],
                    "values": ["Responsibility", "Accuracy"],
                    "pcis": ["Environmental education"]
                },
                {
                    "name": "Area of Part of a Circle",
                    "slos": [
                        {"name": "Calculate area of a sector", "description": "By the end of the sub-strand the learner should be able to calculate the area of a sector."},
                        {"name": "Calculate area of a segment", "description": "By the end of the sub-strand the learner should be able to calculate the area of a segment."},
                        {"name": "Calculate area of combined shapes", "description": "By the end of the sub-strand the learner should be able to calculate the area of combined shapes involving circles."},
                    ],
                    "learning_experiences": [
                        "Calculate area of sectors using the formula",
                        "Calculate area of segments",
                        "Solve problems involving sectors and segments",
                        "Calculate areas of combined circular shapes"
                    ],
                    "inquiry_questions": ["How do we calculate area of parts of a circle?"],
                    "core_competencies": ["Critical thinking and problem solving", "Creativity and imagination"],
                    "values": ["Responsibility", "Accuracy"],
                    "pcis": []
                },
                {
                    "name": "Surface Area and Volume",
                    "slos": [
                        {"name": "Calculate surface area of prisms", "description": "By the end of the sub-strand the learner should be able to calculate surface area of prisms."},
                        {"name": "Calculate surface area of pyramids", "description": "By the end of the sub-strand the learner should be able to calculate surface area of pyramids."},
                        {"name": "Calculate volume of pyramids", "description": "By the end of the sub-strand the learner should be able to calculate volume of pyramids."},
                        {"name": "Calculate surface area and volume of cones", "description": "By the end of the sub-strand the learner should be able to calculate surface area and volume of cones."},
                        {"name": "Calculate surface area and volume of spheres", "description": "By the end of the sub-strand the learner should be able to calculate surface area and volume of spheres."},
                    ],
                    "learning_experiences": [
                        "Derive and use formulae for surface area of prisms",
                        "Calculate surface area and volume of pyramids",
                        "Calculate surface area and volume of cones",
                        "Calculate surface area and volume of spheres",
                        "Apply surface area and volume in real life problems"
                    ],
                    "inquiry_questions": ["How do we calculate surface area and volume of solids?"],
                    "core_competencies": ["Critical thinking and problem solving", "Learning to learn"],
                    "values": ["Responsibility"],
                    "pcis": []
                },
            ]
        },
        {
            "name": "Geometry",
            "substrands": [
                {
                    "name": "Coordinates and Graphs",
                    "slos": [
                        {"name": "Plot points on the Cartesian plane", "description": "By the end of the sub-strand the learner should be able to plot points on the Cartesian plane."},
                        {"name": "Draw linear graphs", "description": "By the end of the sub-strand the learner should be able to draw linear graphs from equations."},
                        {"name": "Determine gradient of a line", "description": "By the end of the sub-strand the learner should be able to determine the gradient of a straight line."},
                        {"name": "Solve simultaneous equations graphically", "description": "By the end of the sub-strand the learner should be able to solve simultaneous linear equations graphically."},
                    ],
                    "learning_experiences": [
                        "Plot points with positive and negative coordinates",
                        "Draw graphs of linear equations",
                        "Calculate gradient from graphs",
                        "Solve simultaneous equations by graphical method"
                    ],
                    "inquiry_questions": ["What is gradient?", "How do we solve equations graphically?"],
                    "core_competencies": ["Critical thinking and problem solving", "Digital literacy"],
                    "values": ["Responsibility", "Accuracy"],
                    "pcis": []
                },
                {
                    "name": "Vectors",
                    "slos": [
                        {"name": "Define and represent vectors", "description": "By the end of the sub-strand the learner should be able to define vectors and represent them."},
                        {"name": "Add and subtract vectors", "description": "By the end of the sub-strand the learner should be able to add and subtract vectors."},
                        {"name": "Multiply vectors by scalars", "description": "By the end of the sub-strand the learner should be able to multiply vectors by scalars."},
                        {"name": "Apply vectors in real life", "description": "By the end of the sub-strand the learner should be able to apply vectors in real life situations."},
                    ],
                    "learning_experiences": [
                        "Define vectors as quantities with magnitude and direction",
                        "Represent vectors using directed line segments",
                        "Add and subtract vectors graphically",
                        "Multiply vectors by scalars"
                    ],
                    "inquiry_questions": ["What are vectors?", "Where do we use vectors?"],
                    "core_competencies": ["Critical thinking and problem solving", "Communication and collaboration"],
                    "values": ["Responsibility"],
                    "pcis": []
                },
                {
                    "name": "Transformations",
                    "slos": [
                        {"name": "Perform translations", "description": "By the end of the sub-strand the learner should be able to perform translations on the Cartesian plane."},
                        {"name": "Perform reflections", "description": "By the end of the sub-strand the learner should be able to perform reflections on the Cartesian plane."},
                        {"name": "Perform rotations", "description": "By the end of the sub-strand the learner should be able to perform rotations about a point."},
                        {"name": "Perform enlargements", "description": "By the end of the sub-strand the learner should be able to perform enlargements with a given scale factor."},
                    ],
                    "learning_experiences": [
                        "Translate shapes on the Cartesian plane",
                        "Reflect shapes in given mirror lines",
                        "Rotate shapes about a given point",
                        "Enlarge shapes with given scale factors"
                    ],
                    "inquiry_questions": ["What are transformations?", "How do transformations change shapes?"],
                    "core_competencies": ["Creativity and imagination", "Critical thinking"],
                    "values": ["Responsibility", "Accuracy"],
                    "pcis": []
                },
            ]
        },
        {
            "name": "Data Handling and Probability",
            "substrands": [
                {
                    "name": "Statistics",
                    "slos": [
                        {"name": "Calculate mean of grouped data", "description": "By the end of the sub-strand the learner should be able to calculate mean of grouped data."},
                        {"name": "Calculate median of grouped data", "description": "By the end of the sub-strand the learner should be able to calculate median of grouped data."},
                        {"name": "Draw cumulative frequency curves", "description": "By the end of the sub-strand the learner should be able to draw cumulative frequency curves (ogives)."},
                        {"name": "Estimate median from ogives", "description": "By the end of the sub-strand the learner should be able to estimate median from cumulative frequency curves."},
                    ],
                    "learning_experiences": [
                        "Calculate mean of grouped data using assumed mean",
                        "Calculate median using cumulative frequency",
                        "Draw cumulative frequency curves",
                        "Estimate median and quartiles from ogives"
                    ],
                    "inquiry_questions": ["How do we analyze grouped data?", "What are cumulative frequency curves?"],
                    "core_competencies": ["Critical thinking and problem solving", "Digital literacy"],
                    "values": ["Responsibility", "Accuracy"],
                    "pcis": []
                },
                {
                    "name": "Probability",
                    "slos": [
                        {"name": "Calculate probability of combined events", "description": "By the end of the sub-strand the learner should be able to calculate probability of combined events."},
                        {"name": "Use probability trees", "description": "By the end of the sub-strand the learner should be able to use probability trees to solve problems."},
                        {"name": "Calculate probability of mutually exclusive events", "description": "By the end of the sub-strand the learner should be able to calculate probability of mutually exclusive events."},
                        {"name": "Calculate probability of independent events", "description": "By the end of the sub-strand the learner should be able to calculate probability of independent events."},
                    ],
                    "learning_experiences": [
                        "Calculate probability of combined events",
                        "Draw and use probability trees",
                        "Apply addition rule for mutually exclusive events",
                        "Apply multiplication rule for independent events"
                    ],
                    "inquiry_questions": ["How do we calculate probability of combined events?"],
                    "core_competencies": ["Critical thinking and problem solving", "Learning to learn"],
                    "values": ["Responsibility", "Integrity"],
                    "pcis": []
                },
            ]
        },
    ]
}


# ============================================================================
# INTEGRATED SCIENCE GRADE 9
# ============================================================================
INTEGRATED_SCIENCE_GRADE_9 = {
    "name": "Integrated Science",
    "strands": [
        {
            "name": "Mixtures, Elements and Compounds",
            "substrands": [
                {
                    "name": "Structure of the Atom",
                    "slos": [
                        {"name": "Describe the structure of the atom", "description": "By the end of the sub-strand the learner should be able to describe the structure of the atom including protons, electrons and neutrons."},
                        {"name": "Determine mass number of elements", "description": "By the end of the sub-strand the learner should be able to determine the mass number of elements."},
                        {"name": "Draw electron arrangement diagrams", "description": "By the end of the sub-strand the learner should be able to draw the electron arrangement in atoms using dot or cross diagrams."},
                        {"name": "Classify elements into metals and non-metals", "description": "By the end of the sub-strand the learner should be able to classify elements into metals and non-metals."},
                    ],
                    "learning_experiences": [
                        "Discuss the meaning of the atom and illustrate its structure",
                        "Work out the mass number of an element with peers",
                        "Write the electron arrangements of elements",
                        "Illustrate the electron arrangement using dot or cross diagrams",
                        "Use electron arrangement to classify elements into metals and non-metals",
                        "Use digital media to observe animations on atomic structure",
                        "Project: Model the atomic structure of selected elements using locally available materials"
                    ],
                    "inquiry_questions": ["How is the structure of the atom important?"],
                    "core_competencies": ["Communication and collaboration - speaking clearly and effectively", "Creativity and imagination - experimenting with models"],
                    "values": ["Unity - respecting others' opinions", "Integrity - displaying honesty when using digital devices"],
                    "pcis": ["Cyber security - observing measures when using digital media"]
                },
                {
                    "name": "Metals and Alloys",
                    "slos": [
                        {"name": "Describe physical properties of metals", "description": "By the end of the sub-strand the learner should be able to describe the physical properties of metals including ductility, malleability, conductivity."},
                        {"name": "Describe composition of alloys", "description": "By the end of the sub-strand the learner should be able to describe the composition of common alloys."},
                        {"name": "Identify uses of metals and alloys", "description": "By the end of the sub-strand the learner should be able to identify the uses of metals and alloys in day to day life."},
                        {"name": "Explain effects of rusting", "description": "By the end of the sub-strand the learner should be able to explain the effects of rusting of metals."},
                    ],
                    "learning_experiences": [
                        "Identify metals and non-metals in the environment",
                        "Carry out experiments to demonstrate physical properties of metals",
                        "Discuss the composition of common alloys with peers",
                        "Identify items made from alloys in the locality",
                        "Discuss the uses of common metals and alloys",
                        "Discuss causes, effects and ways of controlling rusting",
                        "Use digital or print media to search for information on metals and alloys"
                    ],
                    "inquiry_questions": ["How are alloys important in day-to-day life?"],
                    "core_competencies": ["Communication and collaboration - working with peers", "Digital literacy - interacting with digital technology"],
                    "values": ["Respect - accommodating others' opinions", "Peace - avoiding harm during experiments"],
                    "pcis": ["Financial literacy - appreciating importance of metals and alloys"]
                },
                {
                    "name": "Water Hardness",
                    "slos": [
                        {"name": "Describe physical properties of water", "description": "By the end of the sub-strand the learner should be able to describe the physical properties of water."},
                        {"name": "Distinguish hard and soft water", "description": "By the end of the sub-strand the learner should be able to distinguish between hard and soft water in nature."},
                        {"name": "Apply methods of softening hard water", "description": "By the end of the sub-strand the learner should be able to apply methods of softening hard water in day to day life."},
                        {"name": "Outline advantages and disadvantages of hard water", "description": "By the end of the sub-strand the learner should be able to outline advantages and disadvantages of hard and soft water."},
                    ],
                    "learning_experiences": [
                        "Collect and observe water from different sources",
                        "Compare water samples in terms of appearance, odour, taste and boiling point",
                        "Carry out activities to compare lathering abilities of water samples with soap",
                        "Group samples into hard and soft water",
                        "Discuss advantages and disadvantages of soft and hard water",
                        "Perform various activities for softening hard water",
                        "Use digital or print media to search for information"
                    ],
                    "inquiry_questions": ["What is the importance of different types of water?", "Why is hard water preferred for drinking?"],
                    "core_competencies": ["Critical thinking and problem solving", "Communication and collaboration"],
                    "values": ["Responsibility", "Unity"],
                    "pcis": ["Environmental education", "Water conservation"]
                },
            ]
        },
        {
            "name": "Living Things and the Environment",
            "substrands": [
                {
                    "name": "Health and Diseases",
                    "slos": [
                        {"name": "Define health and disease", "description": "By the end of the sub-strand the learner should be able to define health and disease."},
                        {"name": "Classify diseases", "description": "By the end of the sub-strand the learner should be able to classify diseases as communicable and non-communicable."},
                        {"name": "Describe transmission of diseases", "description": "By the end of the sub-strand the learner should be able to describe how communicable diseases are transmitted."},
                        {"name": "Discuss prevention and control of diseases", "description": "By the end of the sub-strand the learner should be able to discuss prevention and control of common diseases."},
                    ],
                    "learning_experiences": [
                        "Define health and disease",
                        "Classify diseases into communicable and non-communicable",
                        "Discuss modes of transmission of common diseases",
                        "Research on common diseases in the community",
                        "Discuss prevention and control measures",
                        "Create awareness on disease prevention"
                    ],
                    "inquiry_questions": ["How do diseases spread?", "How can we prevent diseases?"],
                    "core_competencies": ["Critical thinking and problem solving", "Communication and collaboration"],
                    "values": ["Responsibility", "Social justice"],
                    "pcis": ["Health education", "HIV/AIDS education"]
                },
                {
                    "name": "Genetics and Heredity",
                    "slos": [
                        {"name": "Define heredity and genetics", "description": "By the end of the sub-strand the learner should be able to define heredity and genetics."},
                        {"name": "Describe inheritance of characteristics", "description": "By the end of the sub-strand the learner should be able to describe how characteristics are inherited."},
                        {"name": "Explain variation in living things", "description": "By the end of the sub-strand the learner should be able to explain variation in living things."},
                        {"name": "Discuss genetic disorders", "description": "By the end of the sub-strand the learner should be able to discuss common genetic disorders."},
                    ],
                    "learning_experiences": [
                        "Define heredity and genetics",
                        "Observe and discuss inherited characteristics in families",
                        "Discuss variation in living things",
                        "Research on common genetic disorders",
                        "Discuss management of genetic disorders"
                    ],
                    "inquiry_questions": ["How are characteristics passed from parents to offspring?", "What causes variation?"],
                    "core_competencies": ["Critical thinking and problem solving", "Learning to learn"],
                    "values": ["Respect", "Social justice"],
                    "pcis": ["Health education"]
                },
                {
                    "name": "Biodiversity and Conservation",
                    "slos": [
                        {"name": "Define biodiversity", "description": "By the end of the sub-strand the learner should be able to define biodiversity."},
                        {"name": "Explain importance of biodiversity", "description": "By the end of the sub-strand the learner should be able to explain the importance of biodiversity."},
                        {"name": "Identify threats to biodiversity", "description": "By the end of the sub-strand the learner should be able to identify threats to biodiversity."},
                        {"name": "Discuss conservation measures", "description": "By the end of the sub-strand the learner should be able to discuss conservation measures for biodiversity."},
                    ],
                    "learning_experiences": [
                        "Define biodiversity and its components",
                        "Explore biodiversity in the local environment",
                        "Discuss importance of biodiversity to humans and the environment",
                        "Identify threats to biodiversity",
                        "Research and discuss conservation measures",
                        "Participate in conservation activities"
                    ],
                    "inquiry_questions": ["Why is biodiversity important?", "How can we conserve biodiversity?"],
                    "core_competencies": ["Critical thinking and problem solving", "Citizenship"],
                    "values": ["Responsibility", "Environmental awareness"],
                    "pcis": ["Environmental education", "Conservation"]
                },
            ]
        },
        {
            "name": "Force and Energy",
            "substrands": [
                {
                    "name": "Work, Energy and Power",
                    "slos": [
                        {"name": "Define work, energy and power", "description": "By the end of the sub-strand the learner should be able to define work, energy and power."},
                        {"name": "Calculate work done", "description": "By the end of the sub-strand the learner should be able to calculate work done."},
                        {"name": "Calculate kinetic and potential energy", "description": "By the end of the sub-strand the learner should be able to calculate kinetic and potential energy."},
                        {"name": "Calculate power", "description": "By the end of the sub-strand the learner should be able to calculate power."},
                    ],
                    "learning_experiences": [
                        "Define work, energy and power",
                        "Calculate work done using W = F × d",
                        "Calculate kinetic energy using KE = ½mv²",
                        "Calculate potential energy using PE = mgh",
                        "Calculate power using P = W/t",
                        "Apply concepts in real life situations"
                    ],
                    "inquiry_questions": ["What is the relationship between work, energy and power?"],
                    "core_competencies": ["Critical thinking and problem solving", "Learning to learn"],
                    "values": ["Responsibility"],
                    "pcis": ["Energy conservation"]
                },
                {
                    "name": "Machines",
                    "slos": [
                        {"name": "Define and classify machines", "description": "By the end of the sub-strand the learner should be able to define and classify simple machines."},
                        {"name": "Calculate mechanical advantage", "description": "By the end of the sub-strand the learner should be able to calculate mechanical advantage."},
                        {"name": "Calculate velocity ratio", "description": "By the end of the sub-strand the learner should be able to calculate velocity ratio."},
                        {"name": "Calculate efficiency of machines", "description": "By the end of the sub-strand the learner should be able to calculate efficiency of machines."},
                    ],
                    "learning_experiences": [
                        "Define and classify simple machines: lever, pulley, inclined plane, wheel and axle",
                        "Calculate mechanical advantage of simple machines",
                        "Calculate velocity ratio",
                        "Calculate efficiency using (MA/VR) × 100%",
                        "Investigate factors affecting efficiency"
                    ],
                    "inquiry_questions": ["How do machines make work easier?", "What affects efficiency of machines?"],
                    "core_competencies": ["Critical thinking and problem solving", "Creativity and imagination"],
                    "values": ["Responsibility", "Innovation"],
                    "pcis": []
                },
                {
                    "name": "Electromagnetic Spectrum",
                    "slos": [
                        {"name": "Describe the electromagnetic spectrum", "description": "By the end of the sub-strand the learner should be able to describe the electromagnetic spectrum."},
                        {"name": "Identify types of electromagnetic radiation", "description": "By the end of the sub-strand the learner should be able to identify different types of electromagnetic radiation."},
                        {"name": "Explain uses of electromagnetic radiation", "description": "By the end of the sub-strand the learner should be able to explain uses of different types of electromagnetic radiation."},
                        {"name": "Discuss dangers of electromagnetic radiation", "description": "By the end of the sub-strand the learner should be able to discuss dangers of electromagnetic radiation."},
                    ],
                    "learning_experiences": [
                        "Describe the electromagnetic spectrum",
                        "Identify types: radio waves, microwaves, infrared, visible light, ultraviolet, X-rays, gamma rays",
                        "Discuss properties of each type",
                        "Discuss uses of electromagnetic radiation",
                        "Discuss dangers and safety precautions"
                    ],
                    "inquiry_questions": ["What makes up the electromagnetic spectrum?", "How is electromagnetic radiation used?"],
                    "core_competencies": ["Critical thinking and problem solving", "Digital literacy"],
                    "values": ["Responsibility", "Safety awareness"],
                    "pcis": ["Health education", "Technology"]
                },
            ]
        },
        {
            "name": "Earth and Space",
            "substrands": [
                {
                    "name": "The Earth's Structure",
                    "slos": [
                        {"name": "Describe the structure of the Earth", "description": "By the end of the sub-strand the learner should be able to describe the structure of the Earth."},
                        {"name": "Explain plate tectonics", "description": "By the end of the sub-strand the learner should be able to explain plate tectonics."},
                        {"name": "Describe causes and effects of earthquakes", "description": "By the end of the sub-strand the learner should be able to describe causes and effects of earthquakes."},
                        {"name": "Describe volcanic activity", "description": "By the end of the sub-strand the learner should be able to describe volcanic activity."},
                    ],
                    "learning_experiences": [
                        "Describe layers of the Earth: crust, mantle, core",
                        "Explain plate tectonics and continental drift",
                        "Discuss causes and effects of earthquakes",
                        "Discuss causes and effects of volcanic eruptions",
                        "Research on earthquakes and volcanoes in the region"
                    ],
                    "inquiry_questions": ["What is the structure of the Earth?", "Why do earthquakes and volcanoes occur?"],
                    "core_competencies": ["Critical thinking and problem solving", "Learning to learn"],
                    "values": ["Responsibility", "Safety awareness"],
                    "pcis": ["Disaster risk reduction"]
                },
                {
                    "name": "Stars and Galaxies",
                    "slos": [
                        {"name": "Define stars and galaxies", "description": "By the end of the sub-strand the learner should be able to define stars and galaxies."},
                        {"name": "Describe the life cycle of stars", "description": "By the end of the sub-strand the learner should be able to describe the life cycle of stars."},
                        {"name": "Identify types of galaxies", "description": "By the end of the sub-strand the learner should be able to identify types of galaxies."},
                        {"name": "Discuss space exploration", "description": "By the end of the sub-strand the learner should be able to discuss space exploration."},
                    ],
                    "learning_experiences": [
                        "Define stars and describe their properties",
                        "Describe the life cycle of stars",
                        "Define galaxies and identify types",
                        "Discuss the Milky Way galaxy",
                        "Research on space exploration missions"
                    ],
                    "inquiry_questions": ["What are stars and galaxies?", "How do stars evolve?"],
                    "core_competencies": ["Learning to learn", "Digital literacy"],
                    "values": ["Curiosity", "Appreciation of nature"],
                    "pcis": ["Technology"]
                },
            ]
        },
    ]
}


# ============================================================================
# SOCIAL STUDIES GRADE 9
# ============================================================================
SOCIAL_STUDIES_GRADE_9 = {
    "name": "Social Studies",
    "strands": [
        {
            "name": "Environment and Resources",
            "substrands": [
                {
                    "name": "Energy Resources",
                    "slos": [
                        {"name": "Identify energy resources in Africa", "description": "By the end of the sub-strand the learner should be able to identify energy resources in Africa."},
                        {"name": "Distinguish renewable and non-renewable energy", "description": "By the end of the sub-strand the learner should be able to distinguish between renewable and non-renewable energy sources."},
                        {"name": "Explain importance of energy resources", "description": "By the end of the sub-strand the learner should be able to explain the importance of energy resources."},
                        {"name": "Discuss energy conservation", "description": "By the end of the sub-strand the learner should be able to discuss energy conservation measures."},
                    ],
                    "learning_experiences": [
                        "Identify energy resources in Africa",
                        "Classify energy resources as renewable and non-renewable",
                        "Discuss importance of energy to development",
                        "Research on energy production in Kenya",
                        "Discuss energy conservation measures"
                    ],
                    "inquiry_questions": ["What energy resources are found in Africa?", "How can we conserve energy?"],
                    "core_competencies": ["Critical thinking and problem solving", "Digital literacy"],
                    "values": ["Responsibility", "Environmental awareness"],
                    "pcis": ["Environmental education", "Energy conservation"]
                },
                {
                    "name": "Forestry in Africa",
                    "slos": [
                        {"name": "Identify forest types in Africa", "description": "By the end of the sub-strand the learner should be able to identify forest types in Africa."},
                        {"name": "Explain importance of forests", "description": "By the end of the sub-strand the learner should be able to explain the importance of forests."},
                        {"name": "Identify threats to forests", "description": "By the end of the sub-strand the learner should be able to identify threats to forests."},
                        {"name": "Discuss forest conservation measures", "description": "By the end of the sub-strand the learner should be able to discuss forest conservation measures."},
                    ],
                    "learning_experiences": [
                        "Identify forest types: tropical, temperate, montane",
                        "Discuss distribution of forests in Africa",
                        "Explain importance of forests to economy and environment",
                        "Identify threats to forests: deforestation, fires, pollution",
                        "Discuss conservation measures and afforestation"
                    ],
                    "inquiry_questions": ["Why are forests important?", "How can we conserve forests?"],
                    "core_competencies": ["Critical thinking and problem solving", "Citizenship"],
                    "values": ["Responsibility", "Environmental stewardship"],
                    "pcis": ["Environmental education", "Conservation"]
                },
            ]
        },
        {
            "name": "Economic Development",
            "substrands": [
                {
                    "name": "Industrialization in Africa",
                    "slos": [
                        {"name": "Define industrialization", "description": "By the end of the sub-strand the learner should be able to define industrialization."},
                        {"name": "Identify types of industries", "description": "By the end of the sub-strand the learner should be able to identify types of industries in Africa."},
                        {"name": "Explain factors influencing industrialization", "description": "By the end of the sub-strand the learner should be able to explain factors influencing industrialization."},
                        {"name": "Discuss contribution of industries to economy", "description": "By the end of the sub-strand the learner should be able to discuss contribution of industries to the economy."},
                    ],
                    "learning_experiences": [
                        "Define industrialization",
                        "Identify and classify types of industries",
                        "Discuss factors influencing industrial location",
                        "Research on major industries in Africa",
                        "Discuss contribution of industries to economic development"
                    ],
                    "inquiry_questions": ["What is industrialization?", "Why is industrialization important?"],
                    "core_competencies": ["Critical thinking and problem solving", "Learning to learn"],
                    "values": ["Responsibility", "Innovation"],
                    "pcis": ["Financial literacy", "Career guidance"]
                },
                {
                    "name": "Regional Cooperation",
                    "slos": [
                        {"name": "Identify regional economic organizations", "description": "By the end of the sub-strand the learner should be able to identify regional economic organizations in Africa."},
                        {"name": "Explain objectives of regional organizations", "description": "By the end of the sub-strand the learner should be able to explain objectives of regional economic organizations."},
                        {"name": "Discuss benefits of regional cooperation", "description": "By the end of the sub-strand the learner should be able to discuss benefits of regional economic cooperation."},
                        {"name": "Identify challenges facing regional organizations", "description": "By the end of the sub-strand the learner should be able to identify challenges facing regional organizations."},
                    ],
                    "learning_experiences": [
                        "Identify regional organizations: EAC, ECOWAS, SADC, COMESA",
                        "Discuss objectives and functions of regional organizations",
                        "Analyze benefits of regional cooperation",
                        "Discuss challenges facing regional organizations",
                        "Research on Kenya's role in regional cooperation"
                    ],
                    "inquiry_questions": ["Why is regional cooperation important?", "What challenges face regional organizations?"],
                    "core_competencies": ["Critical thinking and problem solving", "Citizenship"],
                    "values": ["Unity", "Cooperation"],
                    "pcis": ["Peace education", "Regional integration"]
                },
            ]
        },
        {
            "name": "History and Governance",
            "substrands": [
                {
                    "name": "Nationalism and Independence",
                    "slos": [
                        {"name": "Define nationalism", "description": "By the end of the sub-strand the learner should be able to define nationalism."},
                        {"name": "Explain factors that led to nationalism", "description": "By the end of the sub-strand the learner should be able to explain factors that led to rise of nationalism in Africa."},
                        {"name": "Describe nationalist movements", "description": "By the end of the sub-strand the learner should be able to describe nationalist movements in Africa."},
                        {"name": "Discuss attainment of independence", "description": "By the end of the sub-strand the learner should be able to discuss the process of attaining independence."},
                    ],
                    "learning_experiences": [
                        "Define nationalism and its characteristics",
                        "Discuss factors that led to rise of nationalism",
                        "Study nationalist movements in selected African countries",
                        "Research on key nationalist leaders",
                        "Discuss the process of attaining independence"
                    ],
                    "inquiry_questions": ["What led to rise of nationalism in Africa?", "How did African countries gain independence?"],
                    "core_competencies": ["Critical thinking and problem solving", "Communication and collaboration"],
                    "values": ["Patriotism", "Social justice"],
                    "pcis": ["Peace education", "Human rights"]
                },
                {
                    "name": "International Organizations",
                    "slos": [
                        {"name": "Identify international organizations", "description": "By the end of the sub-strand the learner should be able to identify major international organizations."},
                        {"name": "Explain functions of UN", "description": "By the end of the sub-strand the learner should be able to explain the functions of the United Nations."},
                        {"name": "Discuss role of AU", "description": "By the end of the sub-strand the learner should be able to discuss the role of the African Union."},
                        {"name": "Analyze Kenya's participation", "description": "By the end of the sub-strand the learner should be able to analyze Kenya's participation in international organizations."},
                    ],
                    "learning_experiences": [
                        "Identify major international organizations: UN, AU, Commonwealth",
                        "Discuss structure and functions of the United Nations",
                        "Discuss role of African Union in promoting unity",
                        "Research on Kenya's participation in international organizations",
                        "Discuss challenges facing international organizations"
                    ],
                    "inquiry_questions": ["What is the role of international organizations?", "How does Kenya participate?"],
                    "core_competencies": ["Critical thinking and problem solving", "Citizenship"],
                    "values": ["Peace", "Unity", "Cooperation"],
                    "pcis": ["Peace education", "Global citizenship"]
                },
            ]
        },
        {
            "name": "Citizenship and Values",
            "substrands": [
                {
                    "name": "Human Rights",
                    "slos": [
                        {"name": "Define human rights", "description": "By the end of the sub-strand the learner should be able to define human rights."},
                        {"name": "Identify fundamental human rights", "description": "By the end of the sub-strand the learner should be able to identify fundamental human rights."},
                        {"name": "Discuss human rights violations", "description": "By the end of the sub-strand the learner should be able to discuss causes and effects of human rights violations."},
                        {"name": "Explain protection of human rights", "description": "By the end of the sub-strand the learner should be able to explain how human rights are protected."},
                    ],
                    "learning_experiences": [
                        "Define human rights",
                        "Study the Universal Declaration of Human Rights",
                        "Identify fundamental human rights in Kenya's constitution",
                        "Discuss causes and effects of human rights violations",
                        "Research on organizations that protect human rights"
                    ],
                    "inquiry_questions": ["What are human rights?", "How are human rights protected?"],
                    "core_competencies": ["Critical thinking and problem solving", "Citizenship"],
                    "values": ["Respect", "Social justice"],
                    "pcis": ["Human rights", "Peace education"]
                },
                {
                    "name": "Conflict Resolution",
                    "slos": [
                        {"name": "Define conflict", "description": "By the end of the sub-strand the learner should be able to define conflict."},
                        {"name": "Identify types of conflict", "description": "By the end of the sub-strand the learner should be able to identify types of conflict."},
                        {"name": "Explain causes of conflict", "description": "By the end of the sub-strand the learner should be able to explain causes of conflict."},
                        {"name": "Discuss conflict resolution methods", "description": "By the end of the sub-strand the learner should be able to discuss methods of conflict resolution."},
                    ],
                    "learning_experiences": [
                        "Define conflict and identify types",
                        "Discuss causes of conflict at various levels",
                        "Analyze effects of conflict",
                        "Discuss methods of conflict resolution: negotiation, mediation, arbitration",
                        "Role play conflict resolution scenarios"
                    ],
                    "inquiry_questions": ["What causes conflict?", "How can conflicts be resolved?"],
                    "core_competencies": ["Critical thinking and problem solving", "Communication and collaboration"],
                    "values": ["Peace", "Tolerance", "Unity"],
                    "pcis": ["Peace education", "Life skills"]
                },
            ]
        },
    ]
}


# ============================================================================
# ENGLISH GRADE 9
# ============================================================================
ENGLISH_GRADE_9 = {
    "name": "English",
    "strands": [
        {
            "name": "Listening and Speaking",
            "substrands": [
                {
                    "name": "Listening Comprehension",
                    "slos": [
                        {"name": "Listen critically to information", "description": "By the end of the sub-strand the learner should be able to listen critically to information from various sources."},
                        {"name": "Evaluate spoken information", "description": "By the end of the sub-strand the learner should be able to evaluate spoken information for accuracy and relevance."},
                        {"name": "Distinguish fact from opinion", "description": "By the end of the sub-strand the learner should be able to distinguish fact from opinion in spoken texts."},
                    ],
                    "learning_experiences": [
                        "Listen critically to news reports and speeches",
                        "Evaluate information for accuracy and bias",
                        "Distinguish between fact and opinion",
                        "Take notes while listening",
                        "Respond to questions on listened content"
                    ],
                    "inquiry_questions": ["How do we listen critically?", "How do we identify bias?"],
                    "core_competencies": ["Critical thinking and problem solving", "Communication and collaboration"],
                    "values": ["Integrity", "Respect"],
                    "pcis": ["Media literacy"]
                },
                {
                    "name": "Public Speaking",
                    "slos": [
                        {"name": "Prepare and deliver speeches", "description": "By the end of the sub-strand the learner should be able to prepare and deliver speeches effectively."},
                        {"name": "Use appropriate body language", "description": "By the end of the sub-strand the learner should be able to use appropriate body language and voice projection."},
                        {"name": "Respond to audience questions", "description": "By the end of the sub-strand the learner should be able to respond to audience questions confidently."},
                    ],
                    "learning_experiences": [
                        "Research and prepare speeches on various topics",
                        "Practice voice projection and intonation",
                        "Use appropriate gestures and body language",
                        "Deliver speeches to class",
                        "Respond to audience questions"
                    ],
                    "inquiry_questions": ["What makes an effective speaker?", "How do we engage an audience?"],
                    "core_competencies": ["Communication and collaboration", "Self-efficacy"],
                    "values": ["Confidence", "Respect"],
                    "pcis": ["Life skills"]
                },
            ]
        },
        {
            "name": "Reading",
            "substrands": [
                {
                    "name": "Critical Reading",
                    "slos": [
                        {"name": "Analyze author's purpose and perspective", "description": "By the end of the sub-strand the learner should be able to analyze author's purpose and perspective."},
                        {"name": "Evaluate arguments in texts", "description": "By the end of the sub-strand the learner should be able to evaluate arguments and evidence in texts."},
                        {"name": "Compare and contrast texts", "description": "By the end of the sub-strand the learner should be able to compare and contrast different texts on similar topics."},
                    ],
                    "learning_experiences": [
                        "Analyze author's purpose in different texts",
                        "Identify and evaluate arguments and evidence",
                        "Compare different perspectives on same topic",
                        "Identify bias and propaganda techniques",
                        "Write critical responses to texts"
                    ],
                    "inquiry_questions": ["How do we read critically?", "How do we identify author's bias?"],
                    "core_competencies": ["Critical thinking and problem solving", "Learning to learn"],
                    "values": ["Integrity", "Open-mindedness"],
                    "pcis": ["Media literacy"]
                },
                {
                    "name": "Literature Study",
                    "slos": [
                        {"name": "Analyze literary elements", "description": "By the end of the sub-strand the learner should be able to analyze literary elements in texts."},
                        {"name": "Interpret themes and symbols", "description": "By the end of the sub-strand the learner should be able to interpret themes and symbols in literary works."},
                        {"name": "Evaluate literary works", "description": "By the end of the sub-strand the learner should be able to evaluate literary works critically."},
                    ],
                    "learning_experiences": [
                        "Read and analyze set books",
                        "Identify literary elements: plot, character, setting, theme",
                        "Analyze use of literary devices",
                        "Interpret symbols and themes",
                        "Write literary analyses"
                    ],
                    "inquiry_questions": ["How do literary elements contribute to meaning?", "What makes literature valuable?"],
                    "core_competencies": ["Critical thinking and problem solving", "Creativity and imagination"],
                    "values": ["Appreciation of literature", "Cultural awareness"],
                    "pcis": []
                },
            ]
        },
        {
            "name": "Grammar",
            "substrands": [
                {
                    "name": "Advanced Sentence Structures",
                    "slos": [
                        {"name": "Use complex sentence structures", "description": "By the end of the sub-strand the learner should be able to use complex sentence structures effectively."},
                        {"name": "Use subordinate clauses", "description": "By the end of the sub-strand the learner should be able to use subordinate clauses correctly."},
                        {"name": "Apply sentence variety", "description": "By the end of the sub-strand the learner should be able to apply sentence variety in writing."},
                    ],
                    "learning_experiences": [
                        "Construct complex sentences with multiple clauses",
                        "Use noun, adjective and adverb clauses",
                        "Vary sentence structures for effect",
                        "Analyze sentence structures in texts",
                        "Practice sentence combining exercises"
                    ],
                    "inquiry_questions": ["How do complex sentences improve writing?", "When do we use different sentence types?"],
                    "core_competencies": ["Communication and collaboration", "Learning to learn"],
                    "values": ["Clarity", "Precision"],
                    "pcis": []
                },
                {
                    "name": "Reported Speech",
                    "slos": [
                        {"name": "Change direct to reported speech", "description": "By the end of the sub-strand the learner should be able to change direct speech to reported speech."},
                        {"name": "Apply changes in tense and pronouns", "description": "By the end of the sub-strand the learner should be able to apply appropriate changes in tense and pronouns."},
                        {"name": "Report questions and commands", "description": "By the end of the sub-strand the learner should be able to report questions and commands correctly."},
                    ],
                    "learning_experiences": [
                        "Convert direct speech to reported speech",
                        "Apply tense changes correctly",
                        "Change pronouns and time expressions",
                        "Report questions and commands",
                        "Practice with news reports and dialogues"
                    ],
                    "inquiry_questions": ["When do we use reported speech?", "What changes occur in reported speech?"],
                    "core_competencies": ["Communication and collaboration", "Learning to learn"],
                    "values": ["Accuracy"],
                    "pcis": []
                },
            ]
        },
        {
            "name": "Writing",
            "substrands": [
                {
                    "name": "Argumentative Writing",
                    "slos": [
                        {"name": "Write argumentative essays", "description": "By the end of the sub-strand the learner should be able to write well-structured argumentative essays."},
                        {"name": "Develop and support arguments", "description": "By the end of the sub-strand the learner should be able to develop and support arguments with evidence."},
                        {"name": "Address counterarguments", "description": "By the end of the sub-strand the learner should be able to address counterarguments effectively."},
                    ],
                    "learning_experiences": [
                        "Plan argumentative essays",
                        "Develop strong thesis statements",
                        "Support arguments with evidence",
                        "Address and refute counterarguments",
                        "Write persuasive conclusions"
                    ],
                    "inquiry_questions": ["What makes an effective argument?", "How do we persuade readers?"],
                    "core_competencies": ["Critical thinking and problem solving", "Communication and collaboration"],
                    "values": ["Integrity", "Open-mindedness"],
                    "pcis": []
                },
                {
                    "name": "Research Writing",
                    "slos": [
                        {"name": "Conduct research", "description": "By the end of the sub-strand the learner should be able to conduct research using various sources."},
                        {"name": "Cite sources correctly", "description": "By the end of the sub-strand the learner should be able to cite sources correctly."},
                        {"name": "Write research papers", "description": "By the end of the sub-strand the learner should be able to write research papers with proper documentation."},
                    ],
                    "learning_experiences": [
                        "Identify and evaluate sources",
                        "Take notes and organize information",
                        "Cite sources using standard formats",
                        "Write research papers",
                        "Avoid plagiarism"
                    ],
                    "inquiry_questions": ["How do we conduct research?", "Why is citation important?"],
                    "core_competencies": ["Learning to learn", "Digital literacy"],
                    "values": ["Integrity", "Responsibility"],
                    "pcis": ["Academic integrity"]
                },
            ]
        },
    ]
}


# ============================================================================
# KISWAHILI GRADE 9
# ============================================================================
KISWAHILI_GRADE_9 = {
    "name": "Kiswahili",
    "strands": [
        {
            "name": "Kusikiliza na Kuongea",
            "substrands": [
                {
                    "name": "Kusikiliza kwa Makini",
                    "slos": [
                        {"name": "Sikiliza kwa makini habari mbalimbali", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kusikiliza kwa makini habari mbalimbali na kutathmini."},
                        {"name": "Tathmini taarifa zilizozungumzwa", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kutathmini taarifa zilizozungumzwa kwa usahihi."},
                        {"name": "Tofautisha ukweli na maoni", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kutofautisha ukweli na maoni."},
                    ],
                    "learning_experiences": [
                        "Kusikiliza kwa makini habari za redio na televisheni",
                        "Kutathmini taarifa kwa usahihi na upendeleo",
                        "Kutofautisha ukweli na maoni",
                        "Kuandika vidokezo wakati wa kusikiliza",
                        "Kujibu maswali kuhusu yaliyosikilizwa"
                    ],
                    "inquiry_questions": ["Tunawezaje kusikiliza kwa makini?", "Tunawezaje kutambua upendeleo?"],
                    "core_competencies": ["Fikra makini na utatuzi wa matatizo", "Mawasiliano na ushirikiano"],
                    "values": ["Uadilifu", "Heshima"],
                    "pcis": ["Elimu ya vyombo vya habari"]
                },
                {
                    "name": "Uwasilishaji wa Umma",
                    "slos": [
                        {"name": "Andaa na toa hotuba", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kuandaa na kutoa hotuba kwa ufasaha."},
                        {"name": "Tumia lugha ya mwili ipasavyo", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kutumia lugha ya mwili na sauti ipasavyo."},
                        {"name": "Jibu maswali ya wasikilizaji", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kujibu maswali ya wasikilizaji kwa ujasiri."},
                    ],
                    "learning_experiences": [
                        "Kuchunguza na kuandaa hotuba kuhusu mada mbalimbali",
                        "Kufanya mazoezi ya kutumia sauti na lafudhi",
                        "Kutumia ishara na lugha ya mwili ipasavyo",
                        "Kutoa hotuba darasani",
                        "Kujibu maswali ya wasikilizaji"
                    ],
                    "inquiry_questions": ["Ni nini kinachofanya mzungumzaji kuwa bora?", "Tunawezaje kuvutia wasikilizaji?"],
                    "core_competencies": ["Mawasiliano na ushirikiano", "Kujiamini"],
                    "values": ["Ujasiri", "Heshima"],
                    "pcis": ["Stadi za maisha"]
                },
            ]
        },
        {
            "name": "Kusoma",
            "substrands": [
                {
                    "name": "Kusoma kwa Uhakiki",
                    "slos": [
                        {"name": "Changanua madhumuni ya mwandishi", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kuchanganua madhumuni na mtazamo wa mwandishi."},
                        {"name": "Tathmini hoja katika matini", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kutathmini hoja na ushahidi katika matini."},
                        {"name": "Linganisha na kulinganua matini", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kulinganisha na kulinganua matini mbalimbali."},
                    ],
                    "learning_experiences": [
                        "Kuchanganua madhumuni ya mwandishi katika matini mbalimbali",
                        "Kutambua na kutathmini hoja na ushahidi",
                        "Kulinganisha mitazamo tofauti kuhusu mada moja",
                        "Kutambua upendeleo na mbinu za propaganda",
                        "Kuandika majibu ya uhakiki"
                    ],
                    "inquiry_questions": ["Tunawezaje kusoma kwa uhakiki?", "Tunawezaje kutambua upendeleo?"],
                    "core_competencies": ["Fikra makini na utatuzi wa matatizo", "Kujifunza kujifunza"],
                    "values": ["Uadilifu", "Uwazi wa mawazo"],
                    "pcis": ["Elimu ya vyombo vya habari"]
                },
                {
                    "name": "Fasihi",
                    "slos": [
                        {"name": "Changanua vipengele vya fasihi", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kuchanganua vipengele vya fasihi katika kazi za fasihi."},
                        {"name": "Fafanua maudhui na ishara", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kufafanua maudhui na ishara katika kazi za fasihi."},
                        {"name": "Tathmini kazi za fasihi", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kutathmini kazi za fasihi kwa uhakiki."},
                    ],
                    "learning_experiences": [
                        "Kusoma na kuchanganua vitabu teule",
                        "Kutambua vipengele vya fasihi: ploti, wahusika, mandhari, maudhui",
                        "Kuchanganua matumizi ya mbinu za fasihi",
                        "Kufafanua ishara na maudhui",
                        "Kuandika uhakiki wa fasihi"
                    ],
                    "inquiry_questions": ["Vipengele vya fasihi vinachangiaje maana?", "Fasihi ina thamani gani?"],
                    "core_competencies": ["Fikra makini na utatuzi wa matatizo", "Ubunifu na mawazo"],
                    "values": ["Upendaji wa fasihi", "Ufahamu wa kitamaduni"],
                    "pcis": []
                },
            ]
        },
        {
            "name": "Sarufi",
            "substrands": [
                {
                    "name": "Miundo ya Sentensi za Juu",
                    "slos": [
                        {"name": "Tumia miundo changamano ya sentensi", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kutumia miundo changamano ya sentensi kwa ufanisi."},
                        {"name": "Tumia vishazi tegemezi", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kutumia vishazi tegemezi kwa usahihi."},
                        {"name": "Tumia aina mbalimbali za sentensi", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kutumia aina mbalimbali za sentensi katika uandishi."},
                    ],
                    "learning_experiences": [
                        "Kutunga sentensi changamano zenye vishazi vingi",
                        "Kutumia vishazi vya nomino, kivumishi na kielezi",
                        "Kubadilisha miundo ya sentensi kwa matokeo mbalimbali",
                        "Kuchanganua miundo ya sentensi katika matini",
                        "Kufanya mazoezi ya kuunganisha sentensi"
                    ],
                    "inquiry_questions": ["Sentensi changamano zinaboresha uandishi vipi?", "Tunapotumia aina gani za sentensi?"],
                    "core_competencies": ["Mawasiliano na ushirikiano", "Kujifunza kujifunza"],
                    "values": ["Uwazi", "Usahihi"],
                    "pcis": []
                },
                {
                    "name": "Semi za Kiswahili",
                    "slos": [
                        {"name": "Tambua na utumie misemo", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kutambua na kutumia misemo ya Kiswahili."},
                        {"name": "Tambua na utumie methali", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kutambua na kutumia methali kwa usahihi."},
                        {"name": "Tambua na utumie nahau", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kutambua na kutumia nahau katika mawasiliano."},
                    ],
                    "learning_experiences": [
                        "Kutambua misemo ya Kiswahili na maana zake",
                        "Kutumia methali katika mazungumzo na uandishi",
                        "Kutambua na kutumia nahau",
                        "Kuchunguza asili na maana za semi",
                        "Kutunga sentensi kwa kutumia semi"
                    ],
                    "inquiry_questions": ["Semi za Kiswahili zina umuhimu gani?", "Tunazitumia vipi?"],
                    "core_competencies": ["Mawasiliano na ushirikiano", "Ubunifu"],
                    "values": ["Urithi wa kitamaduni"],
                    "pcis": []
                },
            ]
        },
        {
            "name": "Kuandika",
            "substrands": [
                {
                    "name": "Uandishi wa Hoja",
                    "slos": [
                        {"name": "Andika insha za hoja", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kuandika insha za hoja zenye muundo mzuri."},
                        {"name": "Endeleza na uunge mkono hoja", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kuendeleza na kuunga mkono hoja kwa ushahidi."},
                        {"name": "Jibu hoja pinzani", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kujibu hoja pinzani kwa ufanisi."},
                    ],
                    "learning_experiences": [
                        "Kupanga insha za hoja",
                        "Kuendeleza kauli kuu zenye nguvu",
                        "Kuunga mkono hoja kwa ushahidi",
                        "Kujibu na kukanusha hoja pinzani",
                        "Kuandika hitimisho zenye kushawishi"
                    ],
                    "inquiry_questions": ["Ni nini kinachofanya hoja kuwa bora?", "Tunawashawishije wasomaji?"],
                    "core_competencies": ["Fikra makini na utatuzi wa matatizo", "Mawasiliano na ushirikiano"],
                    "values": ["Uadilifu", "Uwazi wa mawazo"],
                    "pcis": []
                },
                {
                    "name": "Uandishi Rasmi",
                    "slos": [
                        {"name": "Andika barua rasmi za aina mbalimbali", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kuandika barua rasmi za aina mbalimbali."},
                        {"name": "Andika ripoti", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kuandika ripoti zenye muundo unaofaa."},
                        {"name": "Andika maombi ya kazi", "description": "Kufikia mwisho wa somo ndogo, mwanafunzi aweze kuandika maombi ya kazi."},
                    ],
                    "learning_experiences": [
                        "Kuandika barua rasmi: za malalamiko, kuomba, kutoa taarifa",
                        "Kuandika ripoti za aina mbalimbali",
                        "Kuandika barua za kuomba kazi na CV",
                        "Kujaza fomu za maombi",
                        "Kuandika barua pepe rasmi"
                    ],
                    "inquiry_questions": ["Uandishi rasmi una sifa gani?", "Kwa nini uandishi rasmi ni muhimu?"],
                    "core_competencies": ["Mawasiliano na ushirikiano", "Ujuzi wa kidijitali"],
                    "values": ["Uwajibikaji", "Usahihi"],
                    "pcis": ["Mwongozo wa kazi", "Stadi za maisha"]
                },
            ]
        },
    ]
}


async def get_existing_subject(subject_name, grade_id):
    """Get existing subject from database"""
    subject = await db.subjects.find_one({
        "name": subject_name,
        "gradeIds": grade_id
    })
    return subject


async def clear_subject_grade_data(subject_id):
    """Clear existing curriculum data (strands, substrands, SLOs, activities) for a subject"""
    # Get all strands
    strands = await db.strands.find({"subjectId": subject_id}).to_list(None)
    
    deleted_stats = {"strands": 0, "substrands": 0, "slos": 0, "activities": 0}
    
    for strand in strands:
        strand_id = str(strand['_id'])
        
        # Get substrands
        substrands = await db.substrands.find({"strandId": strand_id}).to_list(None)
        
        for substrand in substrands:
            substrand_id = str(substrand['_id'])
            
            # Delete SLOs
            result = await db.slos.delete_many({"substrandId": substrand_id})
            deleted_stats["slos"] += result.deleted_count
            
            # Delete activities
            result = await db.learning_activities.delete_many({"substrandId": substrand_id})
            deleted_stats["activities"] += result.deleted_count
        
        # Delete substrands
        result = await db.substrands.delete_many({"strandId": strand_id})
        deleted_stats["substrands"] += result.deleted_count
    
    # Delete strands
    result = await db.strands.delete_many({"subjectId": subject_id})
    deleted_stats["strands"] += result.deleted_count
    
    return deleted_stats


async def seed_subject_curriculum(subject_data, grade_id):
    """Seed curriculum data for an existing subject"""
    subject_name = subject_data["name"]
    print(f"\n{'='*60}")
    print(f"Processing: {subject_name}")
    print(f"{'='*60}")
    
    # Get existing subject
    subject = await get_existing_subject(subject_name, grade_id)
    
    if not subject:
        print(f"  ERROR: Subject '{subject_name}' not found for Grade 9!")
        print(f"  Skipping...")
        return 0, 0, 0, 0
    
    subject_id = str(subject['_id'])
    print(f"  Found existing subject: {subject_id[:20]}...")
    
    # Clear existing data
    deleted = await clear_subject_grade_data(subject_id)
    print(f"  Cleared: {deleted['strands']} strands, {deleted['substrands']} substrands, {deleted['slos']} SLOs, {deleted['activities']} activities")
    
    # Seed new data
    strands_count = 0
    substrands_count = 0
    slos_count = 0
    activities_count = 0
    
    for strand_data in subject_data["strands"]:
        # Create strand
        strand_result = await db.strands.insert_one({
            "name": strand_data["name"],
            "subjectId": subject_id
        })
        strand_id = str(strand_result.inserted_id)
        strands_count += 1
        
        for substrand_data in strand_data["substrands"]:
            # Create substrand
            substrand_result = await db.substrands.insert_one({
                "name": substrand_data["name"],
                "strandId": strand_id
            })
            substrand_id = str(substrand_result.inserted_id)
            substrands_count += 1
            
            # Create SLOs
            for slo_data in substrand_data["slos"]:
                await db.slos.insert_one({
                    "name": slo_data["name"],
                    "description": slo_data["description"],
                    "substrandId": substrand_id
                })
                slos_count += 1
            
            # Create learning activities
            learning_experiences = substrand_data.get("learning_experiences", [])
            if learning_experiences:
                total = len(learning_experiences)
                intro_end = max(1, total // 3)
                dev_end = max(2, 2 * total // 3)
                
                await db.learning_activities.insert_one({
                    "substrandId": substrand_id,
                    "introduction": learning_experiences[:intro_end],
                    "development": learning_experiences[intro_end:dev_end],
                    "conclusion": learning_experiences[dev_end:],
                    "extendedActivities": [],
                    "inquiry_questions": substrand_data.get("inquiry_questions", []),
                    "core_competencies": substrand_data.get("core_competencies", []),
                    "values": substrand_data.get("values", []),
                    "pcis": substrand_data.get("pcis", [])
                })
                activities_count += 1
    
    print(f"  Added: {strands_count} strands, {substrands_count} substrands, {slos_count} SLOs, {activities_count} activities")
    return strands_count, substrands_count, slos_count, activities_count


async def main():
    """Main function to seed Grade 9 curriculum"""
    print("=" * 70)
    print("SEEDING GRADE 9 CURRICULUM FROM UPLOADED PDFs")
    print("=" * 70)
    
    # Get Grade 9
    grade_9 = await db.grades.find_one({"name": "Grade 9"})
    if not grade_9:
        print("ERROR: Grade 9 not found in database!")
        return
    
    grade_9_id = str(grade_9['_id'])
    print(f"Grade 9 ID: {grade_9_id}")
    
    # Subjects to seed
    subjects_data = [
        MATHEMATICS_GRADE_9,
        INTEGRATED_SCIENCE_GRADE_9,
        SOCIAL_STUDIES_GRADE_9,
        ENGLISH_GRADE_9,
        KISWAHILI_GRADE_9,
    ]
    
    total_strands = 0
    total_substrands = 0
    total_slos = 0
    total_activities = 0
    
    for subject_data in subjects_data:
        s, ss, slo, act = await seed_subject_curriculum(subject_data, grade_9_id)
        total_strands += s
        total_substrands += ss
        total_slos += slo
        total_activities += act
    
    print("\n" + "=" * 70)
    print("SEEDING COMPLETE")
    print("=" * 70)
    print(f"Total Strands: {total_strands}")
    print(f"Total Substrands: {total_substrands}")
    print(f"Total SLOs: {total_slos}")
    print(f"Total Activity Sets: {total_activities}")
    
    # Verify
    print("\n=== DATABASE VERIFICATION ===")
    for subject_data in subjects_data:
        subject = await db.subjects.find_one({"name": subject_data["name"], "gradeIds": grade_9_id})
        if subject:
            subject_id = str(subject['_id'])
            strands = await db.strands.count_documents({"subjectId": subject_id})
            print(f"  {subject_data['name']}: {strands} strands")


if __name__ == "__main__":
    asyncio.run(main())
