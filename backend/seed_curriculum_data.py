#!/usr/bin/env python3
"""
Seed curriculum data from KICD PDFs into MongoDB
This script populates the database with curriculum data for Grade 10 subjects:
- Chemistry
- Computer Science
- CSL (Community Service Learning)
- English
- Fasihi ya Kiswahili
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

# Curriculum data extracted from PDFs

CHEMISTRY_DATA = {
    "strands": [
        {
            "name": "Inorganic Chemistry",
            "substrands": [
                {
                    "name": "Introduction to Chemistry",
                    "slos": [
                        {"name": "Explain the meaning of Chemistry as a field of science", "description": "By the end of the lesson, the learner should be able to explain the meaning of Chemistry as a field of science."},
                        {"name": "Explore the role of Chemistry in day to day life", "description": "By the end of the lesson, the learner should be able to explore the role of Chemistry in day to day life."},
                        {"name": "Examine the effects of drug and substance use", "description": "By the end of the lesson, the learner should be able to examine the effects of drug and substance use in day to day life."},
                        {"name": "Promote rights to safe learning environment", "description": "By the end of the lesson, the learner should be able to promote the rights and responsibilities to a safe and healthy learning environment."}
                    ]
                },
                {
                    "name": "The Atom",
                    "slos": [
                        {"name": "Describe the structure of the atom", "description": "By the end of the lesson, the learner should be able to describe the structure of the atom."},
                        {"name": "Determine the relative atomic mass of elements", "description": "By the end of the lesson, the learner should be able to determine the relative atomic mass of elements."},
                        {"name": "Write electron arrangement using s and p notation", "description": "By the end of the lesson, the learner should be able to write the electron arrangement of elements using s and p notation."},
                        {"name": "Develop interest in the study of structure of the atom", "description": "By the end of the lesson, the learner should be able to develop interest in the study of structure of the atom."}
                    ]
                },
                {
                    "name": "The Periodic Table",
                    "slos": [
                        {"name": "Relate element position to electron arrangement", "description": "By the end of the lesson, the learner should be able to relate the position of an element in the periodic table to its electron arrangement."},
                        {"name": "Illustrate ion formation of elements", "description": "By the end of the lesson, the learner should be able to illustrate ion formation of elements."},
                        {"name": "Derive the formulae of compounds", "description": "By the end of the lesson, the learner should be able to derive the formulae of compounds."},
                        {"name": "Write balanced equations for chemical reactions", "description": "By the end of the lesson, the learner should be able to write balanced equations for chemical reactions."},
                        {"name": "Appreciate role of electron arrangement", "description": "By the end of the lesson, the learner should be able to appreciate the role of electron arrangement in the development of the periodic table."}
                    ]
                },
                {
                    "name": "Chemical Bonding",
                    "slos": [
                        {"name": "Illustrate bond types in elements and compounds", "description": "By the end of the lesson, the learner should be able to illustrate bond types in elements, molecules and compounds."},
                        {"name": "Investigate bond types and physical properties", "description": "By the end of the lesson, the learner should be able to investigate the relationship between bond types and physical properties of elements, molecules and compounds."},
                        {"name": "Relate bond types to uses of substances", "description": "By the end of the lesson, the learner should be able to relate bond types and resultant structures to the uses of elements, molecules and compounds."},
                        {"name": "Appreciate uses of substances based on bond types", "description": "By the end of the lesson, the learner should be able to appreciate the uses of different substances based on their bond types and structures in day to day life."}
                    ]
                },
                {
                    "name": "Periodicity",
                    "slos": [
                        {"name": "Describe trends in physical properties", "description": "By the end of the lesson, the learner should be able to describe the trends in physical properties of elements of the periodic table."},
                        {"name": "Investigate chemical properties of elements", "description": "By the end of the lesson, the learner should be able to investigate the chemical properties of elements in group of the periodic table."},
                        {"name": "Describe trends in properties across a period", "description": "By the end of the lesson, the learner should be able to describe the trends in properties across a period."},
                        {"name": "Outline applications of periodic table elements", "description": "By the end of the lesson, the learner should be able to outline applications of elements of the periodic table."},
                        {"name": "Appreciate applications of various elements", "description": "By the end of the lesson, the learner should be able to appreciate applications of various elements of the periodic table."}
                    ]
                }
            ]
        },
        {
            "name": "Physical Chemistry",
            "substrands": [
                {
                    "name": "Acids and Bases",
                    "slos": [
                        {"name": "Explain characteristics of acids and bases", "description": "By the end of the lesson, the learner should be able to explain the characteristics of acids and bases in aqueous solutions."},
                        {"name": "Describe chemical properties of acids and bases", "description": "By the end of the lesson, the learner should be able to describe the chemical properties of acids and bases."},
                        {"name": "Classify acids and bases into strong and weak", "description": "By the end of the lesson, the learner should be able to classify acids and bases into strong and weak using universal indicator."},
                        {"name": "Outline uses of acids and bases", "description": "By the end of the lesson, the learner should be able to outline the uses of acids and bases in day to day life."},
                        {"name": "Appreciate uses of acids and bases", "description": "By the end of the lesson, the learner should be able to appreciate the uses of acids and bases in day to day activities."}
                    ]
                },
                {
                    "name": "Introduction to Salts",
                    "slos": [
                        {"name": "Classify different salts based on properties", "description": "By the end of the lesson, the learner should be able to classify different salts based on their properties."},
                        {"name": "Prepare salts using appropriate methods", "description": "By the end of the lesson, the learner should be able to prepare salts using appropriate methods in the laboratory."},
                        {"name": "Describe behaviour of salts when exposed to air", "description": "By the end of the lesson, the learner should be able to describe the behaviour of salts when exposed to air."},
                        {"name": "Outline applications of salts", "description": "By the end of the lesson, the learner should be able to outline applications of salts in day to day life."},
                        {"name": "Appreciate applications of salts", "description": "By the end of the lesson, the learner should be able to appreciate applications of salts in day to day life."}
                    ]
                }
            ]
        }
    ]
}

COMPUTER_SCIENCE_DATA = {
    "strands": [
        {
            "name": "Foundation of Computer Science",
            "substrands": [
                {
                    "name": "Evolution and Development of Computers",
                    "slos": [
                        {"name": "Identify early computing devices", "description": "By the end of the lesson, the learner should be able to identify early computing devices and how they relate to evolution of electronic computers."},
                        {"name": "Describe principle technologies of computer development", "description": "By the end of the lesson, the learner should be able to describe principle technologies that defined development of computers."},
                        {"name": "Relate technologies to computer generations", "description": "By the end of the lesson, the learner should be able to relate the principle technologies to respective computer generation."},
                        {"name": "Appreciate technological advancement in computers", "description": "By the end of the lesson, the learner should be able to appreciate technological advancement in the development of computers."}
                    ]
                },
                {
                    "name": "Computer Organisation and Architecture",
                    "slos": [
                        {"name": "Describe von Neumann computer organisation", "description": "By the end of the lesson, the learner should be able to describe the functional organisation and architecture of a von Neumann computer."},
                        {"name": "Analyse relationships among functional elements", "description": "By the end of the lesson, the learner should be able to analyse the relationships among functional elements of von Neumann computer."},
                        {"name": "Create a model of computer architecture", "description": "By the end of the lesson, the learner should be able to create a model of a computer architecture depicting the structural elements of a von Neumann computer."},
                        {"name": "Use number systems to represent data", "description": "By the end of the lesson, the learner should be able to use binary, octal and hexadecimal number systems to represent data in a von Neumann's digital computer."},
                        {"name": "Appreciate importance of computer architecture", "description": "By the end of the lesson, the learner should be able to appreciate the importance of computer architecture in computing."}
                    ]
                },
                {
                    "name": "Input/Output (I/O) Devices",
                    "slos": [
                        {"name": "Describe types of input and output devices", "description": "By the end of the lesson, the learner should be able to describe types of input and output devices used in computer systems."},
                        {"name": "Examine criteria for selecting I/O devices", "description": "By the end of the lesson, the learner should be able to examine criteria used in selecting input and output devices."},
                        {"name": "Use input and output devices", "description": "By the end of the lesson, the learner should be able to use input and output devices to perform tasks."},
                        {"name": "Appreciate advancement of I/O devices", "description": "By the end of the lesson, the learner should be able to appreciate the advancement of input and output devices used in computer systems."}
                    ]
                },
                {
                    "name": "Computer Storage",
                    "slos": [
                        {"name": "Identify types of storage", "description": "By the end of the lesson, the learner should be able to identify types of storage used in computer systems."},
                        {"name": "Categorise types of storage", "description": "By the end of the lesson, the learner should be able to categorise types of storage used in computer systems."},
                        {"name": "Read and write data to storage", "description": "By the end of the lesson, the learner should be able to read data from and write data to a computer storage."},
                        {"name": "Establish criteria for selecting storage", "description": "By the end of the lesson, the learner should be able to establish criteria used to select computer storage."},
                        {"name": "Acknowledge safety of data in storage", "description": "By the end of the lesson, the learner should be able to acknowledge safety of data in computer storage media."}
                    ]
                },
                {
                    "name": "Central Processing Unit (CPU)",
                    "slos": [
                        {"name": "Describe structural elements of CPU", "description": "By the end of the lesson, the learner should be able to describe structural elements of the CPU of a computer system."},
                        {"name": "Relate CPU elements to their functions", "description": "By the end of the lesson, the learner should be able to relate structural elements of the CPU to their functions."},
                        {"name": "Examine types of CPUs", "description": "By the end of the lesson, the learner should be able to examine types of CPUs in computing devices."},
                        {"name": "Appreciate the role of CPU", "description": "By the end of the lesson, the learner should be able to appreciate the role of CPU in computing."}
                    ]
                },
                {
                    "name": "Operating System (OS)",
                    "slos": [
                        {"name": "Describe functions of an operating system", "description": "By the end of the lesson, the learner should be able to describe functions of an operating system."},
                        {"name": "Classify operating systems", "description": "By the end of the lesson, the learner should be able to classify operating system according to different attributes."},
                        {"name": "Install an operating system", "description": "By the end of the lesson, the learner should be able to install an operating system in a computer."},
                        {"name": "Use an operating system", "description": "By the end of the lesson, the learner should be able to use an operating system to perform a task."},
                        {"name": "Acknowledge importance of operating systems", "description": "By the end of the lesson, the learner should be able to acknowledge the importance of operating systems in computing."}
                    ]
                },
                {
                    "name": "Computer Setup",
                    "slos": [
                        {"name": "Explain types of ports and cables", "description": "By the end of the lesson, the learner should be able to explain types of ports and cables used in computers."},
                        {"name": "Relate cables to corresponding ports", "description": "By the end of the lesson, the learner should be able to relate cables to their corresponding ports in a computer."},
                        {"name": "Set up a computer for use", "description": "By the end of the lesson, the learner should be able to set up a computer for use."},
                        {"name": "Appreciate correct setup procedure", "description": "By the end of the lesson, the learner should be able to appreciate following the correct procedure when setting up a computer."}
                    ]
                }
            ]
        },
        {
            "name": "Computer Networking",
            "substrands": [
                {
                    "name": "Data Communication",
                    "slos": [
                        {"name": "Define data communication concepts", "description": "By the end of the lesson, the learner should be able to define basic data communications concepts."},
                        {"name": "Describe characteristics of data communication", "description": "By the end of the lesson, the learner should be able to describe characteristics of data communication in computer networking."},
                        {"name": "Analyse components of data communication", "description": "By the end of the lesson, the learner should be able to analyse the components of data communication system."},
                        {"name": "Simulate modes of data flow", "description": "By the end of the lesson, the learner should be able to simulate modes of data flow in communication systems."},
                        {"name": "Acknowledge significance of data communication", "description": "By the end of the lesson, the learner should be able to acknowledge the significance of data communication systems in networking."}
                    ]
                },
                {
                    "name": "Data Transmission Media",
                    "slos": [
                        {"name": "Define data transmission concepts", "description": "By the end of the lesson, the learner should be able to define basic concepts used in data transmission."},
                        {"name": "Describe types of transmission media", "description": "By the end of the lesson, the learner should be able to describe types of transmission media used in computer networks."},
                        {"name": "Connect digital devices for data communication", "description": "By the end of the lesson, the learner should be able to connect digital devices used in data communication."},
                        {"name": "Establish factors affecting network communication", "description": "By the end of the lesson, the learner should be able to establish factors that affect communication over a computer network."},
                        {"name": "Appreciate role of transmission media", "description": "By the end of the lesson, the learner should be able to appreciate the role of transmission media in computer networking."}
                    ]
                },
                {
                    "name": "Computer Network Elements",
                    "slos": [
                        {"name": "Identify types of computer networks", "description": "By the end of the lesson, the learner should be able to identify different types of computer networks."},
                        {"name": "Describe elements of a computer network", "description": "By the end of the lesson, the learner should be able to describe elements of a computer network."},
                        {"name": "Evaluate criteria of a computer network", "description": "By the end of the lesson, the learner should be able to evaluate criteria of a computer network."},
                        {"name": "Connect a device to network", "description": "By the end of the lesson, the learner should be able to connect a computing device to available network."},
                        {"name": "Appreciate role of networks in communication", "description": "By the end of the lesson, the learner should be able to appreciate the role of computer networks in communication."}
                    ]
                },
                {
                    "name": "Network Topologies",
                    "slos": [
                        {"name": "Differentiate network topologies", "description": "By the end of the lesson, the learner should be able to differentiate between physical and logical network topologies."},
                        {"name": "Describe types of topologies", "description": "By the end of the lesson, the learner should be able to describe types of logical and physical topologies in computer networking."},
                        {"name": "Create a physical network topology", "description": "By the end of the lesson, the learner should be able to create a physical network topology for a computer network."},
                        {"name": "Appreciate use of network topologies", "description": "By the end of the lesson, the learner should be able to appreciate the use of network topologies in computer networks."}
                    ]
                }
            ]
        },
        {
            "name": "Software Development",
            "substrands": [
                {
                    "name": "Computer Programming Concepts",
                    "slos": [
                        {"name": "Explain programming terminologies", "description": "By the end of the lesson, the learner should be able to explain the terminologies used in programming languages."},
                        {"name": "Describe evolution of programming languages", "description": "By the end of the lesson, the learner should be able to describe evolution of programming languages in software development."},
                        {"name": "Categorise programming languages", "description": "By the end of the lesson, the learner should be able to categorise the programming languages according to the paradigms."},
                        {"name": "Create simple instructions", "description": "By the end of the lesson, the learner should be able to create simple instructions to simulate low level programming languages."},
                        {"name": "Acknowledge evolution of programming", "description": "By the end of the lesson, the learner should be able to acknowledge the evolution of programming languages in software development."}
                    ]
                },
                {
                    "name": "Program Development",
                    "slos": [
                        {"name": "Describe stages of program development", "description": "By the end of the lesson, the learner should be able to describe stages of program development in computer programming."},
                        {"name": "Write a pseudocode for algorithm", "description": "By the end of the lesson, the learner should be able to write a pseudocode to illustrate the logical flow of an algorithm."},
                        {"name": "Represent algorithm using flowchart", "description": "By the end of the lesson, the learner should be able to represent the logical flow of an algorithm using a flowchart."},
                        {"name": "Design algorithm to solve problems", "description": "By the end of the lesson, the learner should be able to design an algorithm to solve a real life problem."},
                        {"name": "Appreciate algorithms in problem solving", "description": "By the end of the lesson, the learner should be able to appreciate the importance of using algorithms in problem solving."}
                    ]
                },
                {
                    "name": "Identifiers and Operators",
                    "slos": [
                        {"name": "Describe elementary elements of programs", "description": "By the end of the lesson, the learner should be able to describe the elementary elements of a computer program."},
                        {"name": "Declare variables and constants", "description": "By the end of the lesson, the learner should be able to declare variables and constants in a programming language."},
                        {"name": "Use input and output statements", "description": "By the end of the lesson, the learner should be able to use input and output statements in a programming language."},
                        {"name": "Use operators in programming", "description": "By the end of the lesson, the learner should be able to use operators in a programming language."},
                        {"name": "Appreciate identifiers and operators", "description": "By the end of the lesson, the learner should be able to appreciate the role of identifiers and operators in programming."}
                    ]
                },
                {
                    "name": "Control Structures",
                    "slos": [
                        {"name": "Describe control structures", "description": "By the end of the lesson, the learner should be able to describe control structures in programming."},
                        {"name": "Select appropriate control structure", "description": "By the end of the lesson, the learner should be able to select program control structure for a given situation."},
                        {"name": "Use control structures in programming", "description": "By the end of the lesson, the learner should be able to use control structures in programming."},
                        {"name": "Appreciate application of control structures", "description": "By the end of the lesson, the learner should be able to appreciate the application of control structures in programming."}
                    ]
                },
                {
                    "name": "Data Structures",
                    "slos": [
                        {"name": "Describe types of containers", "description": "By the end of the lesson, the learner should be able to describe types of containers in programming."},
                        {"name": "Use containers in programming", "description": "By the end of the lesson, the learner should be able to use containers in programming."},
                        {"name": "Apply sorting and searching techniques", "description": "By the end of the lesson, the learner should be able to apply sorting and searching techniques in data structures."},
                        {"name": "Embrace use of containers", "description": "By the end of the lesson, the learner should be able to embrace the use of containers in programming."}
                    ]
                },
                {
                    "name": "Functions",
                    "slos": [
                        {"name": "Discuss types of functions", "description": "By the end of the lesson, the learner should be able to discuss types of function used in modular programming."},
                        {"name": "Use built-in and user-defined functions", "description": "By the end of the lesson, the learner should be able to use built-in and user-defined functions to create a modular program."},
                        {"name": "Discuss scope and parameter passing", "description": "By the end of the lesson, the learner should be able to discuss the scope of variables and parameter passing between functions."},
                        {"name": "Appreciate modularity in programming", "description": "By the end of the lesson, the learner should be able to appreciate the importance of modularity in programming."}
                    ]
                }
            ]
        }
    ]
}

CSL_DATA = {
    "strands": [
        {
            "name": "Citizenship",
            "substrands": [
                {
                    "name": "Concept of CSL",
                    "slos": [
                        {"name": "Explain principles of CSL", "description": "By the end of the lesson, the learner should be able to explain the principles of CSL as a learning strategy."},
                        {"name": "Outline rationale of CSL", "description": "By the end of the lesson, the learner should be able to outline the rationale of CSL in the learning process."},
                        {"name": "Examine civic identity", "description": "By the end of the lesson, the learner should be able to examine their own civic identity as a member of the community."},
                        {"name": "Examine purpose of CSL", "description": "By the end of the lesson, the learner should be able to examine the purpose of CSL in promoting responsible citizenry."},
                        {"name": "Appreciate benefits of CSL", "description": "By the end of the lesson, the learner should be able to appreciate the benefits of CSL for self and community."}
                    ]
                },
                {
                    "name": "Community Needs",
                    "slos": [
                        {"name": "Categorise community needs", "description": "By the end of the lesson, the learner should be able to categorise various needs in the community."},
                        {"name": "Map community resources", "description": "By the end of the lesson, the learner should be able to map potential community resources for CSL activities."},
                        {"name": "Explore community stakeholders", "description": "By the end of the lesson, the learner should be able to explore various community stakeholders for partnership in CSL activities."},
                        {"name": "Realise vastness of needs and resources", "description": "By the end of the lesson, the learner should be able to realise the vastness of needs and resources within their communities for CSL activities."}
                    ]
                },
                {
                    "name": "Leadership Development",
                    "slos": [
                        {"name": "Examine qualities of effective leader", "description": "By the end of the lesson, the learner should be able to examine qualities of an effective leader."},
                        {"name": "Assess leadership styles", "description": "By the end of the lesson, the learner should be able to assess different styles of leadership relevant to community initiatives."},
                        {"name": "Develop leadership guidelines", "description": "By the end of the lesson, the learner should be able to develop guidelines to govern leadership activities."},
                        {"name": "Apply leadership skills", "description": "By the end of the lesson, the learner should be able to apply leadership skills in executing leadership actions."},
                        {"name": "Recognise need for effective leadership", "description": "By the end of the lesson, the learner should be able to recognise the need for effective leadership in executing CSL activities."}
                    ]
                },
                {
                    "name": "Intercultural Competence",
                    "slos": [
                        {"name": "Analyse intercultural competence", "description": "By the end of the lesson, the learner should be able to analyse the concept of intercultural competence."},
                        {"name": "Participate in intercultural activities", "description": "By the end of the lesson, the learner should be able to participate in intercultural activities in the community."},
                        {"name": "Exhibit positive attitudes towards cultures", "description": "By the end of the lesson, the learner should be able to exhibit positive attitudes towards different cultures."},
                        {"name": "Recognise importance of social cohesion", "description": "By the end of the lesson, the learner should be able to recognise the importance of promoting social cohesion among people of varied cultures."}
                    ]
                }
            ]
        },
        {
            "name": "Life Skills",
            "substrands": [
                {
                    "name": "Self-Awareness in the Community",
                    "slos": [
                        {"name": "Explain factors influencing self-awareness", "description": "By the end of the lesson, the learner should be able to explain factors that influence public self-awareness."},
                        {"name": "Analyse importance of positive public-image", "description": "By the end of the lesson, the learner should be able to analyse the importance of positive public-image."},
                        {"name": "Apply public consciousness", "description": "By the end of the lesson, the learner should be able to apply public consciousness (mindfulness of others) in day-to-day life."},
                        {"name": "Appreciate positive public image", "description": "By the end of the lesson, the learner should be able to appreciate my positive public image in the community."}
                    ]
                },
                {
                    "name": "Conflict Resolution",
                    "slos": [
                        {"name": "Explain conflict situations", "description": "By the end of the lesson, the learner should be able to explain situations in the community where conflicts might arise in day to day life."},
                        {"name": "Discuss approaches of solving conflicts", "description": "By the end of the lesson, the learner should be able to discuss approaches of solving conflicts in the community."},
                        {"name": "Apply strategies of solving conflicts", "description": "By the end of the lesson, the learner should be able to apply strategies of solving conflicts in the community."},
                        {"name": "Appreciate peaceful conflict resolution", "description": "By the end of the lesson, the learner should be able to appreciate peaceful conflict resolution in the community."}
                    ]
                },
                {
                    "name": "Responsible Decision-Making",
                    "slos": [
                        {"name": "Describe decision-making process", "description": "By the end of the lesson, the learner should be able to describe decision-making process in day-to-day life."},
                        {"name": "Evaluate qualities of responsible decisions", "description": "By the end of the lesson, the learner should be able to evaluate qualities of responsible decisions."},
                        {"name": "Make responsible decisions", "description": "By the end of the lesson, the learner should be able to make responsible decisions in daily life."},
                        {"name": "Appreciate responsible decisions", "description": "By the end of the lesson, the learner should be able to appreciate responsible decisions in life."}
                    ]
                }
            ]
        },
        {
            "name": "Action Research",
            "substrands": [
                {
                    "name": "Introduction to Action Research",
                    "slos": [
                        {"name": "Explain meaning of action research", "description": "By the end of the lesson, the learner should be able to explain the meaning of action research."},
                        {"name": "Analyse characteristics of action research", "description": "By the end of the lesson, the learner should be able to analyse the characteristics of action research."},
                        {"name": "Illustrate action research cycle", "description": "By the end of the lesson, the learner should be able to illustrate the cycle of action research."},
                        {"name": "Use action research cycle", "description": "By the end of the lesson, the learner should be able to use action research cycle to address issues in the community."},
                        {"name": "Appreciate action research", "description": "By the end of the lesson, the learner should be able to appreciate action research in addressing challenges in the community."}
                    ]
                },
                {
                    "name": "Problem Identification",
                    "slos": [
                        {"name": "Critique scenarios to identify problems", "description": "By the end of the lesson, the learner should be able to critique given scenarios to identify the problem in a community."},
                        {"name": "Use data collection tools", "description": "By the end of the lesson, the learner should be able to use data collection tools to record the characteristics of the problem identified."},
                        {"name": "Analyse data to determine problem nature", "description": "By the end of the lesson, the learner should be able to analyse simple data to determine the nature and extent of the problem."},
                        {"name": "Document and manage data", "description": "By the end of the lesson, the learner should be able to document and manage data for information dissemination."},
                        {"name": "Appreciate accurate documentation", "description": "By the end of the lesson, the learner should be able to appreciate the importance of accurate documentation for effective problem resolution."}
                    ]
                },
                {
                    "name": "Implementation Process",
                    "slos": [
                        {"name": "Identify viable solution", "description": "By the end of the lesson, the learner should be able to identify a viable solution to address a community problem."},
                        {"name": "Create implementation plan", "description": "By the end of the lesson, the learner should be able to create an implementation plan focusing on the identified solution."},
                        {"name": "Implement the plan", "description": "By the end of the lesson, the learner should be able to implement the plan to address the identified problem."},
                        {"name": "Develop reflective report", "description": "By the end of the lesson, the learner should be able to develop a reflective report on the implemented action."},
                        {"name": "Appreciate implementation process", "description": "By the end of the lesson, the learner should be able to appreciate the process of implementation."}
                    ]
                }
            ]
        },
        {
            "name": "Social Entrepreneurship",
            "substrands": [
                {
                    "name": "Social Entrepreneurship Process",
                    "slos": [
                        {"name": "Distinguish social entrepreneurship", "description": "By the end of the lesson, the learner should be able to distinguish social entrepreneurship from other types of enterprises."},
                        {"name": "Analyse social enterprise development", "description": "By the end of the lesson, the learner should be able to analyse the process of a social enterprise development in the community."},
                        {"name": "Apply approaches to sensitise community", "description": "By the end of the lesson, the learner should be able to apply appropriate approaches to sensitise the community on the benefits of social enterprises."},
                        {"name": "Appreciate benefits of social enterprise", "description": "By the end of the lesson, the learner should be able to appreciate the benefits of social enterprise in the community."}
                    ]
                },
                {
                    "name": "Opportunity Identification",
                    "slos": [
                        {"name": "Assess community needs", "description": "By the end of the lesson, the learner should be able to assess the needs of the community for a social enterprise."},
                        {"name": "Develop social enterprise ideas", "description": "By the end of the lesson, the learner should be able to develop social enterprise ideas for the community."},
                        {"name": "Select viable social enterprise ideas", "description": "By the end of the lesson, the learner should be able to select viable social enterprise ideas with the community."},
                        {"name": "Develop interest in social entrepreneurship", "description": "By the end of the lesson, the learner should be able to develop genuine interest in social entrepreneurship in addressing community issues."}
                    ]
                },
                {
                    "name": "Social Enterprise Planning",
                    "slos": [
                        {"name": "Evaluate planning process", "description": "By the end of the lesson, the learner should be able to evaluate the social enterprise planning process."},
                        {"name": "Develop social enterprise plan", "description": "By the end of the lesson, the learner should be able to develop a social enterprise plan for the opportunity identified."},
                        {"name": "Critique social enterprise plan", "description": "By the end of the lesson, the learner should be able to critique a social enterprise plan for refinement."},
                        {"name": "Value planning for social enterprise", "description": "By the end of the lesson, the learner should be able to value planning for social enterprise in the community."}
                    ]
                },
                {
                    "name": "Resource Mobilisation",
                    "slos": [
                        {"name": "Analyse resource mobilisation", "description": "By the end of the lesson, the learner should be able to analyse the concept of resource mobilisation for social enterprise."},
                        {"name": "Develop low-cost budget", "description": "By the end of the lesson, the learner should be able to develop a low-cost budget for social enterprise development."},
                        {"name": "Plan for resource gathering", "description": "By the end of the lesson, the learner should be able to plan for resource gathering for implementation of a social enterprise plan."},
                        {"name": "Recognize role of resource mobilisation", "description": "By the end of the lesson, the learner should be able to recognize the role of resource mobilisation for social enterprise."}
                    ]
                }
            ]
        }
    ]
}

ENGLISH_DATA = {
    "strands": [
        {
            "name": "Listening and Speaking",
            "substrands": [
                {
                    "name": "Extensive Listening",
                    "slos": [
                        {"name": "Describe characters and events from recordings", "description": "By the end of the lesson, the learner should be able to describe characters, places and memorable events from a recording."},
                        {"name": "Pick key details from recordings", "description": "By the end of the lesson, the learner should be able to listen to a recording and pick key details for general information."},
                        {"name": "Recount story or dialogue", "description": "By the end of the lesson, the learner should be able to recount a story or dialogue in an oral context for enjoyment."},
                        {"name": "Acknowledge role of identifying key information", "description": "By the end of the lesson, the learner should be able to acknowledge the role of identifying key information for lifelong learning."}
                    ]
                },
                {
                    "name": "Etiquette",
                    "slos": [
                        {"name": "Pick out target sounds and etiquette", "description": "By the end of the lesson, the learner should be able to pick out the target sounds and aspects of etiquette in oral or written texts."},
                        {"name": "Use appropriate etiquette", "description": "By the end of the lesson, the learner should be able to use appropriate etiquette in different contexts."},
                        {"name": "Articulate sounds for communication", "description": "By the end of the lesson, the learner should be able to articulate the sounds /ɒ/ and /ɔ:/ for effective communication."},
                        {"name": "Justify accurate pronunciation", "description": "By the end of the lesson, the learner should be able to justify the need for accurate pronunciation in communication."}
                    ]
                },
                {
                    "name": "Critical Listening",
                    "slos": [
                        {"name": "Describe distractions to listening", "description": "By the end of the lesson, the learner should be able to describe various forms of distractions to effective listening in different contexts."},
                        {"name": "Determine speaker and intention", "description": "By the end of the lesson, the learner should be able to determine the speaker, context and intention in varied oral texts."},
                        {"name": "Select key points from audio", "description": "By the end of the lesson, the learner should be able to select key points from an audio text for information."},
                        {"name": "Appreciate critical listening", "description": "By the end of the lesson, the learner should be able to appreciate the importance of critical listening in communication."}
                    ]
                },
                {
                    "name": "Pronunciation and Conversational Skills",
                    "slos": [
                        {"name": "Classify discourse markers", "description": "By the end of the lesson, the learner should be able to classify discourse markers used in a variety of texts."},
                        {"name": "Articulate sounds for oral fluency", "description": "By the end of the lesson, the learner should be able to articulate the sounds /ə/, /ɑ:/ and /ɜ:/ for oral fluency."},
                        {"name": "Use discourse markers", "description": "By the end of the lesson, the learner should be able to use discourse markers to organise ideas during conversations."},
                        {"name": "Apply onomatopoeic words", "description": "By the end of the lesson, the learner should be able to apply onomatopoeic words and idiophones in oral communication."},
                        {"name": "Advocate appropriate idea organisation", "description": "By the end of the lesson, the learner should be able to advocate the need to organise ideas appropriately in oral communication."}
                    ]
                },
                {
                    "name": "Intensive Listening",
                    "slos": [
                        {"name": "Select specific details from text", "description": "By the end of the lesson, the learner should be able to select specific details from a listening text."},
                        {"name": "Use words and phrases from oral text", "description": "By the end of the lesson, the learner should be able to use words and phrases picked from an oral text in a variety of contexts."},
                        {"name": "Advocate discrimination among sounds", "description": "By the end of the lesson, the learner should be able to advocate the need to discriminate among sounds for effective communication."}
                    ]
                },
                {
                    "name": "Non-verbal Cues",
                    "slos": [
                        {"name": "Identify sounds in oral texts", "description": "By the end of the lesson, the learner should be able to identify the sounds /ʌ/, /æ/, /aʊ/ and /əʊ/ in oral texts."},
                        {"name": "Articulate sounds for fluency", "description": "By the end of the lesson, the learner should be able to articulate the sounds /ʌ/, /æ/, /aʊ/ and /əʊ/ for oral fluency."},
                        {"name": "Use nonverbal cues appropriately", "description": "By the end of the lesson, the learner should be able to use nonverbal cues appropriately in oral communication."},
                        {"name": "Acknowledge accurate articulation", "description": "By the end of the lesson, the learner should be able to acknowledge the importance of articulating sounds accurately."}
                    ]
                }
            ]
        },
        {
            "name": "Reading",
            "substrands": [
                {
                    "name": "Reading Fluency",
                    "slos": [
                        {"name": "Preview text and make predictions", "description": "By the end of the lesson, the learner should be able to preview a text and make predictions about characters, people and places for reading fluency."},
                        {"name": "Skim texts to obtain gist", "description": "By the end of the lesson, the learner should be able to skim varied texts while glossing over unknown words to obtain the gist."},
                        {"name": "Scan text for specific details", "description": "By the end of the lesson, the learner should be able to scan a text to obtain specific details."},
                        {"name": "Predict word collocations", "description": "By the end of the lesson, the learner should be able to predict how words collocate for effective communication."},
                        {"name": "Acknowledge importance of reading fluency", "description": "By the end of the lesson, the learner should be able to acknowledge the importance of reading fluency in lifelong learning."}
                    ]
                },
                {
                    "name": "Extensive Reading",
                    "slos": [
                        {"name": "Select text for reading", "description": "By the end of the lesson, the learner should be able to select a text in preparation for reading."},
                        {"name": "Read varied texts for enjoyment", "description": "By the end of the lesson, the learner should be able to read varied texts for enjoyment and general understanding."},
                        {"name": "Recognise role of extensive reading", "description": "By the end of the lesson, the learner should be able to recognise the role of extensive reading in building vocabulary."}
                    ]
                },
                {
                    "name": "Study Skills",
                    "slos": [
                        {"name": "Outline steps in summary making", "description": "By the end of the lesson, the learner should be able to outline steps in summary and note making for improving comprehension."},
                        {"name": "Use SQ4R technique", "description": "By the end of the lesson, the learner should be able to use the SQ4R technique and summary and note making skills for study purposes."},
                        {"name": "Analyse visual information", "description": "By the end of the lesson, the learner should be able to analyse visual information in a reading context."},
                        {"name": "Acknowledge effective study skills", "description": "By the end of the lesson, the learner should be able to acknowledge the importance of using effective study skills in extensive and intensive reading."}
                    ]
                },
                {
                    "name": "Intensive Reading",
                    "slos": [
                        {"name": "Evaluate understanding of text", "description": "By the end of the lesson, the learner should be able to evaluate their understanding of a text for comprehension."},
                        {"name": "Make predictions about text", "description": "By the end of the lesson, the learner should be able to make predictions about events, people and places in a text."},
                        {"name": "Answer questions from text", "description": "By the end of the lesson, the learner should be able to answer direct and inferential questions from a text."},
                        {"name": "Infer meaning of words", "description": "By the end of the lesson, the learner should be able to infer the meaning of words and phrases in a written text."},
                        {"name": "Promote reading comprehension", "description": "By the end of the lesson, the learner should be able to promote the role of reading comprehension in lifelong learning."}
                    ]
                },
                {
                    "name": "Critical Reading",
                    "slos": [
                        {"name": "Identify audience, purpose and attitude", "description": "By the end of the lesson, the learner should be able to explain how to identify the audience, purpose and attitude in a text."},
                        {"name": "Determine audience and purpose in text", "description": "By the end of the lesson, the learner should be able to determine the audience, purpose and attitude in a reading text for clarity."},
                        {"name": "Use phrasal verbs and expressions", "description": "By the end of the lesson, the learner should be able to use transparent phrasal verbs and binomial expressions in sentences."},
                        {"name": "Recognise importance of critical reading", "description": "By the end of the lesson, the learner should be able to recognise the importance of critical and close reading in understanding a text."}
                    ]
                }
            ]
        },
        {
            "name": "Grammar in Use",
            "substrands": [
                {
                    "name": "Word Classes",
                    "slos": [
                        {"name": "Classify nouns in sentences", "description": "By the end of the lesson, the learner should be able to classify nouns in sentences."},
                        {"name": "Recognise types of pronouns", "description": "By the end of the lesson, the learner should be able to recognise the various types of pronouns in varied contexts."},
                        {"name": "Differentiate pronouns and determiners", "description": "By the end of the lesson, the learner should be able to differentiate the use of words as pronouns and determiners in sentences."},
                        {"name": "Use nouns and pronouns correctly", "description": "By the end of the lesson, the learner should be able to use nouns and pronouns in sentences."},
                        {"name": "Acknowledge correct usage", "description": "By the end of the lesson, the learner should be able to acknowledge the importance of the correct usage of nouns, pronouns and determiners for effective communication."}
                    ]
                },
                {
                    "name": "Phrases",
                    "slos": [
                        {"name": "Identify constituents of phrases", "description": "By the end of the lesson, the learner should be able to identify the constituents of the noun phrase and verb phrase for information."},
                        {"name": "Use noun and verb phrases", "description": "By the end of the lesson, the learner should be able to use the noun phrase and verb phrase for fluency in oral and written texts."},
                        {"name": "Advocate correct phrase usage", "description": "By the end of the lesson, the learner should be able to advocate the correct usage of noun phrases and verb phrases in communication."}
                    ]
                },
                {
                    "name": "Clauses",
                    "slos": [
                        {"name": "Pick out clauses in sentences", "description": "By the end of the lesson, the learner should be able to pick out relative and adverbial clauses in sentences."},
                        {"name": "Distinguish clause types", "description": "By the end of the lesson, the learner should be able to distinguish between defining and non-defining relative clauses in a text."},
                        {"name": "Use clauses in varied contexts", "description": "By the end of the lesson, the learner should be able to use relative clauses and adverbial clauses in varied contexts."},
                        {"name": "Advocate correct clause use", "description": "By the end of the lesson, the learner should be able to advocate the correct use of relative clauses and adverbial clauses in sentences."}
                    ]
                },
                {
                    "name": "Sentence Structure",
                    "slos": [
                        {"name": "Analyse sentence patterns", "description": "By the end of the lesson, the learner should be able to analyse the SV, SVO, SVC, SVOO, SVOA patterns in simple sentences."},
                        {"name": "Use simple sentences", "description": "By the end of the lesson, the learner should be able to use simple sentences in oral and written texts."},
                        {"name": "Use compound sentences", "description": "By the end of the lesson, the learner should be able to use compound sentences in oral and written texts."},
                        {"name": "Recognise sentence variety", "description": "By the end of the lesson, the learner should be able to recognise the importance of using a variety of sentences in communication."}
                    ]
                }
            ]
        }
    ]
}

FASIHI_KISWAHILI_DATA = {
    "strands": [
        {
            "name": "Fasihi Simulizi",
            "substrands": [
                {
                    "name": "Utangulizi wa Fasihi Simulizi",
                    "slos": [
                        {"name": "Kueleza maana ya fasihi", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kueleza maana ya fasihi."},
                        {"name": "Kueleza maana ya fasihi simulizi", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kueleza maana ya fasihi simulizi."},
                        {"name": "Kufafanua sifa za fasihi simulizi", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kufafanua sifa za fasihi simulizi."},
                        {"name": "Kujadili umuhimu wa fasihi simulizi", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kujadili umuhimu wa fasihi simulizi katika jamii."},
                        {"name": "Kuchangamkia fasihi simulizi", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kuchangamkia fasihi simulizi katika jamii."}
                    ]
                },
                {
                    "name": "Hadithi - Hekaya na Hurafa",
                    "slos": [
                        {"name": "Kueleza maana ya hekaya na hurafa", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kueleza maana ya hekaya na hurafa."},
                        {"name": "Kufafanua sifa za hekaya na hurafa", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kufafanua sifa za hekaya na hurafa."},
                        {"name": "Kujadili umuhimu wa hekaya na hurafa", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kujadili umuhimu wa hekaya na hurafa katika jamii."},
                        {"name": "Kujadili vipengele vya uwasilishaji", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kujadili vipengele vya uwasilishaji wa hekaya na hurafa."},
                        {"name": "Kuwasilisha hekaya na hurafa", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kuwasilisha hekaya na hurafa akizingatia vipengele vya uwasilishaji."}
                    ]
                },
                {
                    "name": "Semi",
                    "slos": [
                        {"name": "Kueleza maana ya semi", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kueleza maana ya semi katika fasihi simulizi."},
                        {"name": "Kufafanua sifa za semi", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kufafanua sifa za semi katika fasihi simulizi."},
                        {"name": "Kujadili umuhimu wa semi", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kujadili umuhimu wa semi katika jamii."},
                        {"name": "Kuainisha vipera vya semi", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kuainisha vipera vya semi ili kuvibainisha."},
                        {"name": "Kufurahia matumizi ya semi", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kufurahia matumizi ya vipera mbalimbali vya semi katika fasihi simulizi."}
                    ]
                },
                {
                    "name": "Maigizo",
                    "slos": [
                        {"name": "Kueleza dhana ya maigizo", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kueleza dhana ya maigizo katika fasihi simulizi."},
                        {"name": "Kufafanua sifa za maigizo", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kufafanua sifa za maigizo."},
                        {"name": "Kujadili umuhimu wa maigizo", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kujadili umuhimu wa maigizo katika jamii."},
                        {"name": "Kuigiza vipera vya maigizo", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kuigiza vipera vya maigizo ya fasihi simulizi."},
                        {"name": "Kuhangamkia maigizo", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kuhangamkia umuhimu wa maigizo katika jamii yake."}
                    ]
                },
                {
                    "name": "Maghani ya Kawaida",
                    "slos": [
                        {"name": "Kueleza maana ya maghani ya kawaida", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kueleza maana ya maghani ya kawaida kama kipera cha ushairi simulizi."},
                        {"name": "Kueleza aina za maghani", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kueleza maana ya majigambo, pembezi na tondozi kama aina za maghani ya kawaida."},
                        {"name": "Kueleza sifa za maghani", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kueleza sifa za majigambo, pembezi na tondozi kama aina za maghani ya kawaida."},
                        {"name": "Kujadili umuhimu wa maghani", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kujadili umuhimu wa majigambo, pembezi na tondozi katika jamii."},
                        {"name": "Kuchanganua vipengele vya maghani", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kuchanganua vipengele vya majigambo, pembezi na tondozi katika matini."}
                    ]
                }
            ]
        },
        {
            "name": "Ushairi",
            "substrands": [
                {
                    "name": "Uainishaji wa Mashairi",
                    "slos": [
                        {"name": "Kueleza maana ya ushairi", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kueleza maana ya ushairi."},
                        {"name": "Kueleza ushairi arudhi na huru", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kueleza maana ya ushairi arudhi na ushairi huru."},
                        {"name": "Kujadili sifa za ushairi", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kujadili sifa za ushairi arudhi na ushairi huru."},
                        {"name": "Kutambua mashairi katika matini", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kutambua mashairi arudhi na mashairi huru katika matini."},
                        {"name": "Kufafanua dhima ya ushairi", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kufafanua dhima ya ushairi katika jamii."},
                        {"name": "Kuhangamkia aina za mashairi", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kuhangamkia aina mbalimbali za mashairi katika jamii."}
                    ]
                },
                {
                    "name": "Uchambuzi wa Maudhui na Dhamira",
                    "slos": [
                        {"name": "Kuchambua maudhui na dhamira", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kuchambua maudhui na dhamira katika mashairi."},
                        {"name": "Kulinganisha maudhui na dhamira", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kulinganisha na kulinganua maudhui na dhamira katika mashairi mbalimbali."},
                        {"name": "Kufurahia maudhui na dhamira", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kufurahia maudhui na dhamira katika mashairi."}
                    ]
                },
                {
                    "name": "Ushairi Simulizi",
                    "slos": [
                        {"name": "Kueleza maana ya ushairi simulizi", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kueleza maana ya ushairi simulizi ili kuubainisha."},
                        {"name": "Kufafanua sifa za ushairi simulizi", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kufafanua sifa za ushairi simulizi ili kuzipambanua."},
                        {"name": "Kuchambua sifa za ushairi simulizi", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kuchambua sifa za ushairi simulizi katika simulizi."},
                        {"name": "Kujadili dhima za ushairi simulizi", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kujadili dhima za ushairi simulizi katika jamii."},
                        {"name": "Kuhangamkia ushairi simulizi", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kuhangamkia ushairi simulizi katika jamii."}
                    ]
                },
                {
                    "name": "Mtindo - Misemo na Nahau",
                    "slos": [
                        {"name": "Kueleza maana ya misemo na nahau", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kueleza maana ya misemo na nahau ili kuipambanua."},
                        {"name": "Kutambua misemo na nahau", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kutambua misemo na nahau katika matini ya fasihi simulizi."},
                        {"name": "Kujadili vipengele vya misemo na nahau", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kujadili vipengele vya misemo na nahau mbalimbali."},
                        {"name": "Kuchanganua misemo na nahau", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kuchanganua misemo na nahau katika matini."},
                        {"name": "Kutumia misemo na nahau", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kutumia misemo na nahau katika tungo za fasihi simulizi."}
                    ]
                },
                {
                    "name": "Uhuru wa Kishairi",
                    "slos": [
                        {"name": "Kueleza lahaja, utohozi na lugha ya kale", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kueleza maana ya lahaja, utohozi na lugha ya kale kama vipengele vya uhuru wa kishairi."},
                        {"name": "Kutambua matumizi ya lahaja na utohozi", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kutambua matumizi ya lahaja, utohozi na lugha ya kale katika mashairi."},
                        {"name": "Kujadili umuhimu wa lahaja na utohozi", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kujadili umuhimu wa lahaja, utohozi na lugha ya kale katika mashairi."},
                        {"name": "Kuchambua mashairi kwa lahaja na utohozi", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kuchambua mashairi kwa kuzingatia matumizi ya lahaja, utohozi na lugha ya kale."},
                        {"name": "Kufurahia matumizi ya lahaja na utohozi", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kufurahia matumizi ya lahaja, utohozi na lugha ya kale katika mashairi."}
                    ]
                }
            ]
        },
        {
            "name": "Bunilizi",
            "substrands": [
                {
                    "name": "Tamthilia - Maudhui na Dhamira",
                    "slos": [
                        {"name": "Kueleza maudhui na dhamira", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kueleza maana ya maudhui na dhamira katika fasihi."},
                        {"name": "Kutambua maudhui na dhamira katika tamthilia", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kutambua maudhui na dhamira mbalimbali katika tamthilia teule."},
                        {"name": "Kujadili maudhui na dhamira", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kujadili na wenzake maudhui na dhamira ya tamthilia teule."},
                        {"name": "Kuwasilisha uchambuzi", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kuwawasilishia wenzake darasani uchambuzi wake kuhusu maudhui."},
                        {"name": "Kuandika maelezo kuhusu maudhui", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kuandika maelezo mafupi kuhusu maudhui katika tamthilia teule."}
                    ]
                },
                {
                    "name": "Tamthilia - Wahusika na Mandhari",
                    "slos": [
                        {"name": "Kueleza wahusika na mandhari", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kueleza dhana ya wahusika na mandhari katika riwaya."},
                        {"name": "Kutambua wahusika na mandhari", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kutambua wahusika na mandhari katika tamthilia teule."},
                        {"name": "Kujadili sifa za wahusika", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kujadili sifa za wahusika katika tamthilia teule."},
                        {"name": "Kueleza umuhimu wa wahusika", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kueleza umuhimu wa wahusika na mandhari katika tamthilia teule."},
                        {"name": "Kujadili mbinu za usawiri", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kujadili mbinu za usawiri wa wahusika katika tamthilia teule."}
                    ]
                },
                {
                    "name": "Tamthilia - Muundo na Mtindo",
                    "slos": [
                        {"name": "Kueleza muundo na mtindo", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kueleza maana ya muundo na mtindo katika tamthilia."},
                        {"name": "Kutambua vipengele vya muundo na mtindo", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kutambua vipengele vya muundo na mtindo katika tamthilia."},
                        {"name": "Kujadili vipengele vya muundo na mtindo", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kujadili vipengele vya muundo na mtindo katika tamthilia teule."},
                        {"name": "Kutathmini nafasi ya vipengele", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kutathmini nafasi ya vipengele vya muundo na mtindo katika tamthilia teule."},
                        {"name": "Kuchambua tamthilia", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kuchambua tamthilia teule kwa kuzingatia muundo na mtindo wake."}
                    ]
                },
                {
                    "name": "Riwaya - Maudhui na Dhamira",
                    "slos": [
                        {"name": "Kueleza maudhui na dhamira katika riwaya", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kueleza maana ya maudhui na dhamira katika riwaya teule."},
                        {"name": "Kutambua maudhui na dhamira", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kutambua maudhui na dhamira katika riwaya teule."},
                        {"name": "Kueleza namna maudhui yanavyowasilishwa", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kueleza namna maudhui yanavyowasilishwa katika riwaya."},
                        {"name": "Kuchanganua maudhui na dhamira", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kuchanganua maudhui na dhamira katika riwaya teule."},
                        {"name": "Kuhangamkia maudhui na dhamira", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kuhangamkia maudhui na dhamira katika riwaya."}
                    ]
                },
                {
                    "name": "Riwaya - Wahusika na Mandhari",
                    "slos": [
                        {"name": "Kueleza wahusika na mandhari katika riwaya", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kueleza dhana ya wahusika na mandhari katika riwaya."},
                        {"name": "Kujadili usawiri wa wahusika", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kujadili usawiri wa wahusika katika riwaya teule."},
                        {"name": "Kueleza umuhimu wa wahusika", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kueleza umuhimu wa wahusika katika riwaya."},
                        {"name": "Kueleza umuhimu wa mandhari", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kueleza umuhimu wa mandhari katika riwaya."},
                        {"name": "Kujadili aina za mandhari", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kujadili aina za mandhari katika riwaya."}
                    ]
                },
                {
                    "name": "Riwaya - Muundo na Mtindo",
                    "slos": [
                        {"name": "Kueleza muundo na mtindo katika riwaya", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kueleza maana ya muundo na mtindo katika riwaya."},
                        {"name": "Kujadili vipengele vya muundo na mtindo", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kujadili vipengele vya muundo na mtindo katika fasihi."},
                        {"name": "Kuchanganua muundo na mtindo", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kuchanganua muundo na mtindo katika riwaya."},
                        {"name": "Kuhangamkia muundo na mtindo", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kuhangamkia muundo na mtindo katika riwaya."}
                    ]
                },
                {
                    "name": "Utunzi wa Mashairi na Bunilizi",
                    "slos": [
                        {"name": "Kutambua vipengele vya utunzi", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kutambua vipengele vya utunzi wa mashairi na bunilizi ili kuvibainisha."},
                        {"name": "Kupambanua hatua za utunzi", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kupambanua hatua za utunzi wa mashairi na bunilizi ili kuzitambulisha."},
                        {"name": "Kuandika shairi au bunilizi", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kuandika shairi au bunilizi fupi kwa kuzingatia vipengele na hatua za utunzi wa kazi ya fasihi."},
                        {"name": "Kuonea fahari utunzi wa bunilizi", "description": "Kufikia mwisho wa somo, mwanafunzi ataweza kuonea fahari utunzi wa bunilizi katika maisha ya kila siku."}
                    ]
                }
            ]
        }
    ]
}

async def get_subject_id(subject_name, grade_id):
    """Get or create subject and return its ID"""
    subject = await db.subjects.find_one({"name": subject_name, "gradeIds": grade_id})
    if not subject:
        # Create subject
        result = await db.subjects.insert_one({
            "name": subject_name,
            "gradeIds": [grade_id]
        })
        return str(result.inserted_id)
    return str(subject["_id"])

async def seed_subject_data(subject_name, curriculum_data, grade_id):
    """Seed curriculum data for a subject"""
    print(f"\n=== Seeding {subject_name} ===")
    
    # Get or create subject
    subject_id = await get_subject_id(subject_name, grade_id)
    print(f"Subject ID: {subject_id}")
    
    # Clear existing data for this subject
    existing_strands = await db.strands.find({"subjectId": subject_id}).to_list(100)
    for strand in existing_strands:
        strand_id = str(strand["_id"])
        # Delete substrands and SLOs
        substrands = await db.substrands.find({"strandId": strand_id}).to_list(100)
        for substrand in substrands:
            substrand_id = str(substrand["_id"])
            await db.slos.delete_many({"substrandId": substrand_id})
        await db.substrands.delete_many({"strandId": strand_id})
    await db.strands.delete_many({"subjectId": subject_id})
    print(f"Cleared existing data for {subject_name}")
    
    # Insert new strands, substrands, and SLOs
    strand_count = 0
    substrand_count = 0
    slo_count = 0
    
    for strand_data in curriculum_data["strands"]:
        # Insert strand
        strand_result = await db.strands.insert_one({
            "name": strand_data["name"],
            "subjectId": subject_id
        })
        strand_id = str(strand_result.inserted_id)
        strand_count += 1
        
        for substrand_data in strand_data["substrands"]:
            # Insert substrand
            substrand_result = await db.substrands.insert_one({
                "name": substrand_data["name"],
                "strandId": strand_id
            })
            substrand_id = str(substrand_result.inserted_id)
            substrand_count += 1
            
            # Insert SLOs
            for slo_data in substrand_data["slos"]:
                await db.slos.insert_one({
                    "name": slo_data["name"],
                    "description": slo_data["description"],
                    "substrandId": substrand_id
                })
                slo_count += 1
    
    print(f"Added: {strand_count} strands, {substrand_count} substrands, {slo_count} SLOs")
    return {"strands": strand_count, "substrands": substrand_count, "slos": slo_count}

async def main():
    """Main function to seed all curriculum data"""
    print("=" * 60)
    print("KICD Curriculum Data Seeding Script")
    print("=" * 60)
    
    # Get Grade 10 ID
    grade_10 = await db.grades.find_one({"name": "Grade 10"})
    if not grade_10:
        # Create Grade 10 if it doesn't exist
        result = await db.grades.insert_one({"name": "Grade 10", "order": 10})
        grade_10_id = str(result.inserted_id)
        print("Created Grade 10")
    else:
        grade_10_id = str(grade_10["_id"])
        print(f"Found Grade 10: {grade_10_id}")
    
    # Seed all subjects
    total_stats = {"strands": 0, "substrands": 0, "slos": 0}
    
    subjects_to_seed = [
        ("Chemistry", CHEMISTRY_DATA),
        ("Computer Science", COMPUTER_SCIENCE_DATA),
        ("Community Service Learning", CSL_DATA),
        ("English", ENGLISH_DATA),
        ("Fasihi ya Kiswahili", FASIHI_KISWAHILI_DATA)
    ]
    
    for subject_name, curriculum_data in subjects_to_seed:
        stats = await seed_subject_data(subject_name, curriculum_data, grade_10_id)
        total_stats["strands"] += stats["strands"]
        total_stats["substrands"] += stats["substrands"]
        total_stats["slos"] += stats["slos"]
    
    print("\n" + "=" * 60)
    print("SEEDING COMPLETE")
    print("=" * 60)
    print(f"Total Strands: {total_stats['strands']}")
    print(f"Total Substrands: {total_stats['substrands']}")
    print(f"Total SLOs: {total_stats['slos']}")
    
    # Verify final counts
    print("\n=== Final Database Counts ===")
    grades_count = await db.grades.count_documents({})
    subjects_count = await db.subjects.count_documents({})
    strands_count = await db.strands.count_documents({})
    substrands_count = await db.substrands.count_documents({})
    slos_count = await db.slos.count_documents({})
    
    print(f"Grades: {grades_count}")
    print(f"Subjects: {subjects_count}")
    print(f"Strands: {strands_count}")
    print(f"Substrands: {substrands_count}")
    print(f"SLOs: {slos_count}")

if __name__ == "__main__":
    asyncio.run(main())
