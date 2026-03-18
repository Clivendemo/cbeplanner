"""
Seed script for Grade 10 curriculum data from 5 subject PDFs:
Arabic, Aviation Technology, Building Construction, Business Studies, Chemistry
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')

async def seed():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client['cbe_lesson_planner']

    # --- STEP 1: Clear old Grade 10 data if exists ---
    old_grade = await db.grades.find_one({"name": {"$regex": "Grade 10", "$options": "i"}})
    if old_grade:
        grade_id = str(old_grade["_id"])
        # Find subjects linked to this grade
        old_subjects = await db.subjects.find({"gradeIds": grade_id}).to_list(500)
        for subj in old_subjects:
            sid = str(subj["_id"])
            old_strands = await db.strands.find({"subjectId": sid}).to_list(500)
            for strand in old_strands:
                stid = str(strand["_id"])
                old_subs = await db.substrands.find({"strandId": stid}).to_list(500)
                for sub in old_subs:
                    ssid = str(sub["_id"])
                    old_slos = await db.slos.find({"substrandId": ssid}).to_list(500)
                    for slo in old_slos:
                        slo_id = str(slo["_id"])
                        await db.slo_mappings.delete_many({"sloId": slo_id})
                    await db.slos.delete_many({"substrandId": ssid})
                    await db.learning_activities.delete_many({"substrandId": ssid})
                await db.substrands.delete_many({"strandId": stid})
            await db.strands.delete_many({"subjectId": sid})
        # Remove grade from subjects
        for subj in old_subjects:
            remaining_grades = [g for g in subj.get("gradeIds", []) if g != grade_id]
            if remaining_grades:
                await db.subjects.update_one({"_id": subj["_id"]}, {"$set": {"gradeIds": remaining_grades}})
            else:
                await db.subjects.delete_one({"_id": subj["_id"]})
        await db.grades.delete_one({"_id": old_grade["_id"]})
        print("Cleared old Grade 10 data")

    # --- STEP 2: Seed default competencies, values, PCIs if not exist ---
    default_competencies = [
        {"name": "Communication and Collaboration", "description": "Ability to communicate effectively and work collaboratively with others"},
        {"name": "Critical Thinking and Problem Solving", "description": "Ability to think critically and solve problems creatively"},
        {"name": "Creativity and Imagination", "description": "Ability to think creatively and generate innovative ideas"},
        {"name": "Citizenship", "description": "Understanding and fulfilling civic responsibilities"},
        {"name": "Digital Literacy", "description": "Ability to use digital technologies effectively"},
        {"name": "Learning to Learn", "description": "Ability to learn independently and manage own learning"},
        {"name": "Self-efficacy", "description": "Confidence in one's ability to succeed in specific situations"}
    ]
    for comp in default_competencies:
        exists = await db.competencies.find_one({"name": comp["name"]})
        if not exists:
            await db.competencies.insert_one(comp)
    print(f"Competencies seeded")

    default_values = [
        {"name": "Responsibility", "description": "Being accountable for one's actions and decisions"},
        {"name": "Respect", "description": "Showing regard for others, self, and the environment"},
        {"name": "Integrity", "description": "Being honest and having strong moral principles"},
        {"name": "Unity", "description": "Working together harmoniously towards common goals"},
        {"name": "Peace", "description": "Promoting harmonious coexistence and conflict resolution"},
        {"name": "Love", "description": "Showing care and compassion for others"},
        {"name": "Social Justice", "description": "Advocating for fairness and equity in society"},
        {"name": "Patriotism", "description": "Showing love and devotion to one's country"}
    ]
    for val in default_values:
        exists = await db.values.find_one({"name": val["name"]})
        if not exists:
            await db.values.insert_one(val)
    print(f"Values seeded")

    default_pcis = [
        {"name": "Life Skills", "description": "Skills needed for effective daily living including safety, self-esteem, and analytical thinking"},
        {"name": "Citizenship", "description": "Understanding civic duties and responsibilities"},
        {"name": "Health Promotion Issues", "description": "Awareness of drug and substance use, health education"},
        {"name": "Socio-Economic and Environmental Issues", "description": "Environmental conservation, consumer protection, social cohesion, global citizenship"},
        {"name": "Learner Support Programmes", "description": "Healthy inter and intra personal relationships and learner support"}
    ]
    for pci in default_pcis:
        exists = await db.pcis.find_one({"name": pci["name"]})
        if not exists:
            await db.pcis.insert_one(pci)
    print(f"PCIs seeded")

    # --- STEP 3: Create Grade 10 ---
    max_order_grade = await db.grades.find_one(sort=[("order", -1)])
    next_order = (max_order_grade["order"] + 1) if max_order_grade else 10
    grade_result = await db.grades.insert_one({"name": "Grade 10", "order": next_order})
    grade_id = str(grade_result.inserted_id)
    print(f"Created Grade 10: {grade_id}")

    # Helper to create SLO mapping
    async def create_slo_mapping(slo_id, assessment_text=""):
        comp_names = ["Communication and Collaboration", "Critical Thinking and Problem Solving", "Learning to Learn"]
        comp_ids = []
        for n in comp_names:
            c = await db.competencies.find_one({"name": n})
            if c: comp_ids.append(str(c["_id"]))

        val_names = ["Responsibility", "Respect", "Integrity"]
        val_ids = []
        for n in val_names:
            v = await db.values.find_one({"name": n})
            if v: val_ids.append(str(v["_id"]))

        pci_names = ["Life Skills", "Citizenship"]
        pci_ids = []
        for n in pci_names:
            p = await db.pcis.find_one({"name": n})
            if p: pci_ids.append(str(p["_id"]))

        assessment_ids = []
        if assessment_text:
            a_result = await db.assessments.insert_one({"name": "Suggested Evaluation", "description": assessment_text})
            assessment_ids.append(str(a_result.inserted_id))

        await db.slo_mappings.insert_one({
            "sloId": slo_id,
            "competencyIds": comp_ids,
            "valueIds": val_ids,
            "pciIds": pci_ids,
            "assessmentIds": assessment_ids
        })

    # Helper to seed a subject
    async def seed_subject(name, strands_data):
        # Check if subject exists, create or update
        existing = await db.subjects.find_one({"name": name})
        if existing:
            await db.subjects.update_one({"_id": existing["_id"]}, {"$addToSet": {"gradeIds": grade_id}})
            subject_id = str(existing["_id"])
        else:
            result = await db.subjects.insert_one({"name": name, "gradeIds": [grade_id]})
            subject_id = str(result.inserted_id)
        print(f"  Subject: {name} ({subject_id})")

        for s_idx, strand_data in enumerate(strands_data):
            strand_result = await db.strands.insert_one({
                "name": strand_data["name"],
                "subjectId": subject_id,
                "order": s_idx + 1
            })
            strand_id = str(strand_result.inserted_id)
            print(f"    Strand: {strand_data['name']}")

            for ss_idx, ss_data in enumerate(strand_data["substrands"]):
                ss_result = await db.substrands.insert_one({
                    "name": ss_data["name"],
                    "strandId": strand_id,
                    "order": ss_idx + 1
                })
                ss_id = str(ss_result.inserted_id)

                # Add learning activities with assessment methods
                if ss_data.get("assessment_methods"):
                    await db.learning_activities.insert_one({
                        "substrandId": ss_id,
                        "introduction_activities": [],
                        "development_activities": [],
                        "conclusion_activities": [],
                        "extended_activities": [],
                        "learning_resources": [],
                        "assessment_methods": ss_data["assessment_methods"]
                    })

                for slo_idx, slo_data in enumerate(ss_data["slos"]):
                    slo_result = await db.slos.insert_one({
                        "name": slo_data["name"],
                        "description": slo_data.get("description", ""),
                        "substrandId": ss_id,
                        "order": slo_idx + 1
                    })
                    slo_id = str(slo_result.inserted_id)
                    await create_slo_mapping(slo_id, slo_data.get("assessment", ""))

        return subject_id

    # ============================================================
    # ARABIC
    # ============================================================
    print("\nSeeding Arabic...")
    arabic_strands = [
        {
            "name": "1.0 Listening and Speaking",
            "substrands": [
                {
                    "name": "1.1 Listening Comprehension",
                    "assessment_methods": ["Role play", "Discussions", "Observations", "Projects", "Learning logs", "Quizzes", "Portfolios", "Multiple choices", "Exit or Admit stamps", "Total Physical Response", "Peer assessment"],
                    "slos": [
                        {"name": "Identify Arabic letters and their sounds for comprehension", "description": "identify Arabic letters and their sounds for comprehension", "assessment": "Exceeds: Uses all targeted vocabulary and expressions to probe and engage in oral interactions and attempts synonymous ones. Meets: Uses all targeted vocabulary and expressions. Approaches: Uses some targeted vocabulary. Below: Uses very few targeted vocabulary."},
                        {"name": "Combine syllables and sounds to form words", "description": "combine syllables and sounds to form words"},
                        {"name": "Respond to simple oral questions appropriately", "description": "respond to simple oral questions appropriately"},
                        {"name": "Develop interest in learning the Arabic language", "description": "develop interest in learning the Arabic language"}
                    ]
                },
                {
                    "name": "1.2 Oral Presentations",
                    "assessment_methods": ["Role play", "Discussions", "Observations", "Quizzes", "Portfolios"],
                    "slos": [
                        {"name": "Express opinions and ideas orally on a given context", "description": "express opinions and ideas orally on a given context"},
                        {"name": "Make a short speech for effective communication", "description": "make a short speech for effective communication"},
                        {"name": "Appreciate presenting ideas orally to convey a message", "description": "appreciate presenting ideas orally to convey a message"}
                    ]
                },
                {
                    "name": "1.3 Speaking Fluency",
                    "assessment_methods": ["Role play", "Discussions", "Observations", "Quizzes"],
                    "slos": [
                        {"name": "Express opinions and ideas fluently", "description": "express opinions and ideas fluently"},
                        {"name": "Use appropriate stress and intonation to describe places", "description": "use appropriate stress and intonation to describe places"},
                        {"name": "Respond fluently to given instructions", "description": "respond fluently to given instructions"},
                        {"name": "Acknowledge fluency speaking in communication", "description": "acknowledge fluency speaking in communication"}
                    ]
                },
                {
                    "name": "1.4 Attentive Listening",
                    "assessment_methods": ["Discussions", "Observations", "Quizzes", "Portfolios"],
                    "slos": [
                        {"name": "Identify specific details from a text for comprehension", "description": "identify specific details from a text for comprehension"},
                        {"name": "Listen to variety of texts to obtain information", "description": "listen to variety of texts to obtain information"},
                        {"name": "Appreciate the importance of listening attentively for lifelong learning", "description": "appreciate the importance of listening attentively for lifelong learning"}
                    ]
                },
                {
                    "name": "1.5 Selective Listening",
                    "assessment_methods": ["Discussions", "Observations", "Quizzes"],
                    "slos": [
                        {"name": "Pick out target vocabulary from an oral text for information", "description": "pick out target vocabulary from an oral text for information"},
                        {"name": "Listen to selected texts to deduce specific information", "description": "listen to selected texts to deduce specific information"},
                        {"name": "Acknowledge the significance of selective listening in communication", "description": "acknowledge the significance of selective listening in communication"}
                    ]
                },
                {
                    "name": "1.6 Listening for Gist",
                    "assessment_methods": ["Discussions", "Observations", "Quizzes", "Peer assessment"],
                    "slos": [
                        {"name": "Identify the main idea from a text", "description": "identify the main idea from a text"},
                        {"name": "Paraphrase a text for specific information", "description": "paraphrase a text for specific information"},
                        {"name": "Acknowledge the importance of listening skills in communication", "description": "acknowledge the importance of listening skills in communication"}
                    ]
                }
            ]
        },
        {
            "name": "2.0 Reading",
            "substrands": [
                {
                    "name": "2.1 Reading for Comprehension",
                    "assessment_methods": ["Reading aloud", "Discussions", "Observations", "Quizzes", "Portfolio", "Reading for fluency"],
                    "slos": [
                        {"name": "Identify the main ideas in a text", "description": "identify the main ideas in a text", "assessment": "Exceeds: Interprets all questions in context and gives correct answers. Uses extensive vocabulary. Meets: Interprets all questions and gives correct answers with adequate vocabulary. Approaches: Interprets most questions with mostly sufficient vocabulary. Below: Interprets few questions with insufficient vocabulary."},
                        {"name": "Respond to questions from a text for comprehension", "description": "respond to questions from a text for comprehension"},
                        {"name": "Summarise information from a short text", "description": "summarise information from a short text"},
                        {"name": "Appreciate the importance of reading for comprehension in lifelong learning", "description": "appreciate the importance of reading for comprehension in lifelong learning"}
                    ]
                },
                {
                    "name": "2.2 Reading Fluency",
                    "assessment_methods": ["Reading aloud", "Discussions", "Observations", "Quizzes"],
                    "slos": [
                        {"name": "Identify the techniques of reading fluently", "description": "identify the techniques of reading fluently"},
                        {"name": "Read a text with correct intonation, stress and pronunciation", "description": "read a text with correct intonation, stress and pronunciation"},
                        {"name": "Apply appropriate expression when reading a text for fluency", "description": "apply appropriate expression when reading a text for fluency"},
                        {"name": "Appreciate the importance of reading fluency for understanding", "description": "appreciate the importance of reading fluency for understanding"}
                    ]
                },
                {
                    "name": "2.3 Reading for Information",
                    "assessment_methods": ["Reading aloud", "Discussions", "Quizzes"],
                    "slos": [
                        {"name": "Identify main information from a text", "description": "identify main information from a text"},
                        {"name": "Infer meaning of vocabulary or phrases for language acquisition", "description": "infer meaning of vocabulary or phrases for language acquisition"},
                        {"name": "Appreciate the importance of reading as a source of information", "description": "appreciate the importance of reading as a source of information"}
                    ]
                },
                {
                    "name": "2.4 Intensive Reading: Poetry",
                    "assessment_methods": ["Reading aloud", "Discussions", "Observations", "Quizzes"],
                    "slos": [
                        {"name": "Read poems fluently for enjoyment", "description": "read poems fluently for enjoyment"},
                        {"name": "Analyse Arabic poems based on the subject matter for information", "description": "analyse Arabic poems based on the subject matter for information"},
                        {"name": "Develop interest in reading Arabic poems for enjoyment", "description": "develop interest in reading Arabic poems for enjoyment"}
                    ]
                },
                {
                    "name": "2.5 Extensive Reading: Library Skills",
                    "assessment_methods": ["Reading aloud", "Discussions", "Portfolio"],
                    "slos": [
                        {"name": "Read simple Arabic texts for enjoyment", "description": "read simple Arabic texts for enjoyment"},
                        {"name": "Track reading progress for lifelong learning", "description": "track reading progress for lifelong learning"},
                        {"name": "Develop a positive reading culture for lifelong learning", "description": "develop a positive reading culture for lifelong learning"}
                    ]
                },
                {
                    "name": "2.6 Intensive Reading: Arabic Prose",
                    "assessment_methods": ["Reading aloud", "Discussions", "Observations", "Quizzes"],
                    "slos": [
                        {"name": "Describe the characteristics of Arabic prose", "description": "describe the characteristics of Arabic prose"},
                        {"name": "Describe characters in a prose text for information", "description": "describe characters in a prose text for information"},
                        {"name": "Discuss prose texts by author and events for information", "description": "discuss prose texts by author and events for information"},
                        {"name": "Value the role of prose in culture transmission", "description": "value the role of prose in culture transmission"}
                    ]
                }
            ]
        },
        {
            "name": "3.0 Writing",
            "substrands": [
                {
                    "name": "3.1 Handwriting",
                    "assessment_methods": ["Writing texts", "Forming sentences", "Peer assessment", "Observations", "Matching names to pictures", "Filling in missing information"],
                    "slos": [
                        {"name": "Trace letters of the Arabic Alphabet neatly and legibly for comprehension", "description": "trace letters of the Arabic Alphabet neatly and legibly for comprehension", "assessment": "Exceeds: Writes readable texts with correct spacing. Text looks like typed document. Meets: Writes readable texts with correct spacing throughout. Approaches: Writes readable texts with some abnormal spacing. Below: Writes texts not easily readable with frequent abnormal spacing."},
                        {"name": "Rewrite words, phrases and sentences neatly for accuracy", "description": "rewrite words, phrases and sentences neatly for accuracy"},
                        {"name": "Appreciate the significance of neatness and legibility in writing", "description": "appreciate the significance of neatness and legibility in writing"}
                    ]
                },
                {
                    "name": "3.2 Mechanics of Writing: Spelling",
                    "assessment_methods": ["Writing texts", "Forming sentences", "Peer assessment", "Observations"],
                    "slos": [
                        {"name": "Identify vocabulary related to the theme for language acquisition", "description": "identify vocabulary related to the theme for language acquisition"},
                        {"name": "Write texts using correct spelling for comprehension", "description": "write texts using correct spelling for comprehension"},
                        {"name": "Acknowledge the role of spelling in communication", "description": "acknowledge the role of spelling in communication"}
                    ]
                },
                {
                    "name": "3.3 Creative Writing: Sequencing Ideas",
                    "assessment_methods": ["Writing texts", "Forming sentences", "Observations", "Matching of sentences"],
                    "slos": [
                        {"name": "Express ideas and opinions in a logical and coherent manner", "description": "express ideas and opinions in a logical and coherent manner"},
                        {"name": "Use connectors of sequence to organise ideas for effective communication", "description": "use connectors of sequence to organise ideas for effective communication"},
                        {"name": "Construct logical and coherent paragraphs for information", "description": "construct logical and coherent paragraphs for information"},
                        {"name": "Appreciate the skill of organising ideas for effective communication", "description": "appreciate the skill of organising ideas for effective communication"}
                    ]
                },
                {
                    "name": "3.4 Descriptive Writing",
                    "assessment_methods": ["Writing texts", "Observations", "Peer assessment"],
                    "slos": [
                        {"name": "Identify descriptive words for information", "description": "identify descriptive words for information"},
                        {"name": "Compose a short descriptive text about a person, thing or place", "description": "compose a short descriptive text about a person, thing or place"},
                        {"name": "Appreciate the importance of descriptive writing in communication", "description": "appreciate the importance of descriptive writing in communication"}
                    ]
                },
                {
                    "name": "3.5 Creative Writing",
                    "assessment_methods": ["Writing texts", "Forming sentences", "Observations"],
                    "slos": [
                        {"name": "Outline vocabulary related to the theme for language acquisition", "description": "outline vocabulary related to the theme for language acquisition"},
                        {"name": "Write short imaginative texts based on the theme", "description": "write short imaginative texts based on the theme"},
                        {"name": "Appreciate the significance of creative writing in communication", "description": "appreciate the significance of creative writing in communication"}
                    ]
                },
                {
                    "name": "3.6 Functional Writing: Informal Letter",
                    "assessment_methods": ["Writing texts", "Observations", "Peer assessment", "Writing menus", "Designing brochures"],
                    "slos": [
                        {"name": "Identify an informal letter by structure and format for comprehension", "description": "identify an informal letter by structure and format for comprehension"},
                        {"name": "Write an informal letter following the correct format", "description": "write an informal letter following the correct format"},
                        {"name": "Develop interest in writing informal letters for communication", "description": "develop interest in writing informal letters for communication"}
                    ]
                }
            ]
        },
        {
            "name": "4.0 Grammar",
            "substrands": [
                {
                    "name": "4.1 Word Class: Nouns",
                    "assessment_methods": ["Observations", "Writing texts", "Construction of sentences", "Designing games", "Discussions", "Role play", "Checklists", "Quizzes"],
                    "slos": [
                        {"name": "Identify nouns in terms of definiteness, gender, singular, dual and plural forms", "description": "identify nouns in terms of their definiteness, gender, singular, dual and plural forms", "assessment": "Exceeds: Excellent use of grammar, variety of punctuation marks, spelling and capitalization. Errors are so few and minor they do not impede reading. Meets: Good use of grammar, punctuation, spelling and capitalization with few errors. Approaches: Moderate errors of grammar, punctuation, spelling that can impede reading. Below: Many errors throughout; reader can only guess meaning."},
                        {"name": "Use nouns featuring definiteness, gender, singular, dual and plural to construct sentences correctly", "description": "use nouns featuring definiteness, gender, singular, dual and plural to construct sentences correctly"},
                        {"name": "Appreciate the significance of nouns in language acquisition", "description": "appreciate the significance of nouns in language acquisition"}
                    ]
                },
                {
                    "name": "4.2 Word Class: Pronouns and Conjunctions",
                    "assessment_methods": ["Observations", "Writing texts", "Construction of sentences", "Discussions", "Quizzes"],
                    "slos": [
                        {"name": "Identify pronouns and conjunctions in texts", "description": "identify pronouns and conjunctions in texts"},
                        {"name": "Use pronouns and conjunctions correctly in sentences", "description": "use pronouns and conjunctions correctly in sentences"},
                        {"name": "Value the use of pronouns and conjunctions in communication", "description": "value the use of pronouns and conjunctions in communication"}
                    ]
                },
                {
                    "name": "4.3 Word Class: Pronouns and Articles",
                    "assessment_methods": ["Observations", "Writing texts", "Construction of sentences", "Discussions", "Quizzes"],
                    "slos": [
                        {"name": "Identify demonstrative pronouns and interrogative articles in a variety of texts", "description": "identify demonstrative pronouns and interrogative articles in a variety of texts"},
                        {"name": "Use demonstrative pronouns and interrogative articles correctly in sentences", "description": "use demonstrative pronouns and interrogative articles correctly in sentences"},
                        {"name": "Appreciate the use of correct demonstrative pronouns and interrogative articles for communication", "description": "appreciate the use of correct demonstrative pronouns and interrogative articles for communication"}
                    ]
                },
                {
                    "name": "4.4 Word Class: Adverbs, Prepositions and Adjectives",
                    "assessment_methods": ["Observations", "Writing texts", "Construction of sentences", "Discussions", "Quizzes", "Checklists"],
                    "slos": [
                        {"name": "Identify adverbs, prepositions and adjectives from a reading text", "description": "identify adverbs, prepositions and adjectives from a reading text"},
                        {"name": "Use adverbs, prepositions and adjectives correctly in sentences", "description": "use adverbs, prepositions and adjectives correctly in sentences"},
                        {"name": "Appreciate the importance of using adverbs, prepositions and adjectives correctly for lifelong learning", "description": "appreciate the importance of using adverbs, prepositions and adjectives correctly for lifelong learning"}
                    ]
                },
                {
                    "name": "4.5 Word Class: Verbs",
                    "assessment_methods": ["Observations", "Writing texts", "Construction of sentences", "Discussions", "Role play", "Quizzes"],
                    "slos": [
                        {"name": "Identify the past, present and imperative verb forms", "description": "identify the past, present and imperative verb forms"},
                        {"name": "Apply past tense, present and imperative verb forms correctly", "description": "apply past tense, present and imperative verb forms correctly"},
                        {"name": "Acknowledge the significance of tense in language learning", "description": "acknowledge the significance of tense in language learning"}
                    ]
                },
                {
                    "name": "4.6 Sentence Patterns",
                    "assessment_methods": ["Observations", "Writing texts", "Construction of sentences", "Discussions", "Quizzes"],
                    "slos": [
                        {"name": "Identify sentences featuring the subject and predicate", "description": "identify sentences featuring the subject and predicate"},
                        {"name": "Use the sentence patterns correctly", "description": "use the sentence patterns correctly"},
                        {"name": "Acknowledge the use of correct sentence patterns in communication", "description": "acknowledge the use of correct sentence patterns in communication"}
                    ]
                }
            ]
        }
    ]
    await seed_subject("Arabic", arabic_strands)

    # ============================================================
    # AVIATION TECHNOLOGY
    # ============================================================
    print("\nSeeding Aviation Technology...")
    aviation_strands = [
        {
            "name": "1.0 Foundations of Aviation Technology",
            "substrands": [
                {
                    "name": "1.1 Introduction to Aviation Technology",
                    "assessment_methods": ["Observation schedule", "Checklist", "Written test", "Rubrics", "Project"],
                    "slos": [
                        {"name": "Explain the historical milestones in the development of aircraft", "description": "explain the historical milestones in the development of aircraft", "assessment": "Exceeds: Comprehensively explains the historical milestones in the development of aircraft. Meets: Explains the historical milestones. Approaches: Explains leaving out a few details. Below: Explains leaving out many details."},
                        {"name": "Relate the contribution of key pioneers to the development of aircraft", "description": "relate the contribution of key pioneers to the development of aircraft"},
                        {"name": "Categorise the types of aircraft in aviation", "description": "categorise the types of aircraft in aviation"},
                        {"name": "Demonstrate heavier and lighter-than-air aircraft in aviation", "description": "demonstrate heavier and lighter-than-air aircraft in aviation"},
                        {"name": "Evaluate the functions of different types of aircraft in aviation", "description": "evaluate the functions of different types of aircraft in aviation"},
                        {"name": "Appreciate the milestones of aircraft development in the aviation industry", "description": "appreciate the milestones of aircraft development in the aviation industry"}
                    ]
                },
                {
                    "name": "1.2 Safety in the Aviation Workplace",
                    "assessment_methods": ["Observation schedule", "Checklist", "Written test", "Rubrics", "Practical work"],
                    "slos": [
                        {"name": "Explain the general rules related to personal safety in the aviation workplace", "description": "explain the general rules related to personal safety in the aviation workplace", "assessment": "Exceeds: Systematically performs first aid procedures related to injuries. Meets: Performs first aid procedures. Approaches: Performs leaving out a few steps. Below: Performs leaving out many steps."},
                        {"name": "Describe the hazards related to personal safety in the aviation workplace", "description": "describe the hazards related to personal safety in the aviation workplace"},
                        {"name": "Classify common injuries related to safety in the aviation workplace", "description": "classify common injuries related to safety in the aviation workplace"},
                        {"name": "Perform first aid procedures related to injuries in the aviation workplace", "description": "perform first aid procedures related to injuries in the aviation workplace"},
                        {"name": "Appreciate the role of safety in the aviation workplace", "description": "appreciate the role of safety in the aviation workplace"}
                    ]
                },
                {
                    "name": "1.3 Airport Safety",
                    "assessment_methods": ["Observation schedule", "Checklist", "Written test", "Rubrics", "Practical work", "Project"],
                    "slos": [
                        {"name": "Explain the safety measures in the main areas of an airport", "description": "explain the safety measures in the main areas of an airport", "assessment": "Exceeds: Systematically demonstrates general safety measures related to movement in an airport. Meets: Demonstrates the general safety measures. Approaches: Demonstrates leaving out a few steps. Below: Demonstrates leaving out many steps."},
                        {"name": "Classify the common safety signs in the main areas of the airport", "description": "classify the common safety signs in the main areas of the airport"},
                        {"name": "Describe the general safety rules related to movement in the main areas of an airport", "description": "describe the general safety rules related to movement in the main areas of an airport"},
                        {"name": "Demonstrate the general safety measures related to movement in an airport", "description": "demonstrate the general safety measures related to movement in an airport"},
                        {"name": "Appreciate the careers related to safety in an airport", "description": "appreciate the careers related to safety in an airport"}
                    ]
                }
            ]
        },
        {
            "name": "2.0 Aircraft Basic Construction",
            "substrands": [
                {
                    "name": "2.1 Aircraft Components",
                    "assessment_methods": ["Observation schedule", "Checklist", "Written test", "Rubrics", "Project"],
                    "slos": [
                        {"name": "Explain the functions of the parts of an aircraft in aviation", "description": "explain the functions of the parts of an aircraft in aviation", "assessment": "Exceeds: Comprehensively explains the functions of the major parts of an aircraft. Meets: Explains the functions. Approaches: Explains a few functions. Below: Explains with assistance."},
                        {"name": "Illustrate the parts of an aircraft in aviation", "description": "illustrate the parts of an aircraft in aviation"},
                        {"name": "Model a heavier-than-air aircraft in aviation", "description": "model a heavier-than-air aircraft in aviation"},
                        {"name": "Appreciate the role of different parts in the operation of an aircraft in aviation", "description": "appreciate the role of different parts in the operation of an aircraft in aviation"}
                    ]
                },
                {
                    "name": "2.2 Aircraft Tools and Materials",
                    "assessment_methods": ["Observation schedule", "Checklist", "Written test", "Rubrics", "Practical work"],
                    "slos": [
                        {"name": "Explain the properties of common materials used in aircraft construction", "description": "explain the properties of common materials used in aircraft construction", "assessment": "Exceeds: Consistently uses aircraft tools to perform given tasks. Meets: Uses aircraft tools to perform given tasks. Approaches: Sometimes uses aircraft tools. Below: Uses aircraft tools with assistance."},
                        {"name": "Describe the functions of aircraft tools used in aircraft construction", "description": "describe the functions of aircraft tools used in aircraft construction"},
                        {"name": "Describe the safety precautions observed in the use of aircraft tools in workshop practice", "description": "describe the safety precautions observed in the use of aircraft tools in workshop practice"},
                        {"name": "Create a model of a heavier than air aircraft in aviation", "description": "create a model of a heavier than air aircraft in aviation"},
                        {"name": "Maintain tools in aircraft construction", "description": "maintain tools in aircraft construction"},
                        {"name": "Appreciate the use of tools and materials in aircraft construction", "description": "appreciate the use of tools and materials in aircraft construction"}
                    ]
                },
                {
                    "name": "2.3 Aircraft Related Drawing: Isometric Drawing",
                    "assessment_methods": ["Observation schedule", "Checklist", "Written test", "Rubrics", "Practical work", "Portfolio"],
                    "slos": [
                        {"name": "Explain the characteristics of isometric drawing in aircraft construction", "description": "explain the characteristics of isometric drawing in aircraft construction", "assessment": "Exceeds: Distinctively draws to scale aircraft parts in orthographic projection. Meets: Draws to scale aircraft parts. Approaches: Draws leaving out a few details. Below: Draws with assistance."},
                        {"name": "Sketch aircraft components in isometric projection", "description": "sketch aircraft components in isometric projection"},
                        {"name": "Draw shaped blocks in isometric projection", "description": "draw shaped blocks in isometric projection"},
                        {"name": "Dimension isometric drawings in aircraft construction", "description": "dimension isometric drawings in aircraft construction"},
                        {"name": "Appreciate the application of isometric projection in aircraft construction", "description": "appreciate the application of isometric projection in aircraft construction"}
                    ]
                }
            ]
        },
        {
            "name": "3.0 Flight Operations",
            "substrands": [
                {
                    "name": "3.1 Aviation Weather",
                    "assessment_methods": ["Observation schedule", "Checklist", "Written test", "Rubrics", "Practical work"],
                    "slos": [
                        {"name": "Explain the elements of weather in the atmosphere", "description": "explain the elements of weather in the atmosphere", "assessment": "Exceeds: Describes and cites examples of the effects of weather on aircraft in flight. Meets: Describes the effects. Approaches: Describes a few effects. Below: Describes with assistance."},
                        {"name": "Describe the effects of the elements of weather on an aircraft in flight", "description": "describe the effects of the elements of weather on an aircraft in flight"},
                        {"name": "Analyse the types of clouds in flight operations", "description": "analyse the types of clouds in flight operations"},
                        {"name": "Measure the elements of weather in flight operations", "description": "measure the elements of weather in flight operations"},
                        {"name": "Appreciate the role of aviation weather in flight operations", "description": "appreciate the role of aviation weather in flight operations"}
                    ]
                },
                {
                    "name": "3.2 Aviation Communication",
                    "assessment_methods": ["Observation schedule", "Checklist", "Written test", "Rubrics", "Practical work"],
                    "slos": [
                        {"name": "Identify the ICAO phonetics in aviation communication", "description": "identify the ICAO phonetics in aviation communication", "assessment": "Exceeds: Consistently interprets standard words and phrases. Meets: Interprets standard words and phrases. Approaches: Sometimes interprets standard words and phrases. Below: Interprets with guidance."},
                        {"name": "Interpret standard words and phrases in aviation communication", "description": "interpret standard words and phrases in aviation communication"},
                        {"name": "Describe the transmission techniques used in aviation communication", "description": "describe the transmission techniques used in aviation communication"},
                        {"name": "Perform aircraft marshalling signals in aviation communication", "description": "perform aircraft marshalling signals in aviation communication"},
                        {"name": "Appreciate the careers related to aviation communication in aviation industry", "description": "appreciate the careers related to aviation communication in aviation industry"}
                    ]
                },
                {
                    "name": "3.3 Aerodynamics of Flight",
                    "assessment_methods": ["Observation schedule", "Checklist", "Written test", "Rubrics", "Practical work"],
                    "slos": [
                        {"name": "Identify the physical properties of the atmosphere", "description": "identify the physical properties of the atmosphere", "assessment": "Exceeds: Critically analyses the forces that act on an aircraft in flight. Meets: Analyses the forces. Approaches: Analyses leaving out a few details. Below: Analyses with assistance."},
                        {"name": "Explain the characteristics of the lower layers of the atmosphere", "description": "explain the characteristics of the lower layers of the atmosphere"},
                        {"name": "Illustrate the axes of an aircraft in theory of flight", "description": "illustrate the axes of an aircraft in theory of flight"},
                        {"name": "Demonstrate the motion of an aircraft about its axes", "description": "demonstrate the motion of an aircraft about its axes"},
                        {"name": "Evaluate the forces that act on an aircraft in flight", "description": "evaluate the forces that act on an aircraft in flight"},
                        {"name": "Acknowledge the effects of aerodynamic forces on an aircraft in flight", "description": "acknowledge the effects of aerodynamic forces on an aircraft in flight"}
                    ]
                }
            ]
        },
        {
            "name": "4.0 Airport Operations",
            "substrands": [
                {
                    "name": "4.1 The Airport",
                    "assessment_methods": ["Observation schedule", "Checklist", "Written test", "Rubrics", "Project"],
                    "slos": [
                        {"name": "Describe the categories of airports in aviation", "description": "describe the categories of airports in aviation", "assessment": "Exceeds: Explains and cites examples of the major areas of an airport. Meets: Explains the functions. Approaches: Explains a few functions. Below: Explains with assistance."},
                        {"name": "Explain the functions of the major areas of an airport", "description": "explain the functions of the major areas of an airport"},
                        {"name": "Illustrate the arrangement of an airport layout in aviation", "description": "illustrate the arrangement of an airport layout in aviation"},
                        {"name": "Model a layout of the physical components of an airport", "description": "model a layout of the physical components of an airport"},
                        {"name": "Appreciate the role of an airport in the economy", "description": "appreciate the role of an airport in the economy"}
                    ]
                },
                {
                    "name": "4.2 Airport Business Services",
                    "assessment_methods": ["Observation schedule", "Checklist", "Written test", "Rubrics", "Project"],
                    "slos": [
                        {"name": "Identify key business services in airport operations", "description": "identify key business services in airport operations", "assessment": "Exceeds: Critically analyses the rights of consumers in airport operations. Meets: Analyses the rights. Approaches: Analyses a few rights. Below: Analyses with assistance."},
                        {"name": "Explain the services offered by key businesses in airport operations", "description": "explain the services offered by key businesses in airport operations"},
                        {"name": "Describe the financial concepts in aviation business services", "description": "describe the financial concepts in aviation business services"},
                        {"name": "Analyse the rights of consumers in airport operations", "description": "analyse the rights of consumers in airport operations"},
                        {"name": "Evaluate the roles of consumer protection agencies in airport operations", "description": "evaluate the roles of consumer protection agencies in airport operations"},
                        {"name": "Recognize the role of aviation businesses in airport operations", "description": "recognize the role of aviation businesses in airport operations"}
                    ]
                }
            ]
        }
    ]
    await seed_subject("Aviation Technology", aviation_strands)

    # ============================================================
    # BUILDING CONSTRUCTION
    # ============================================================
    print("\nSeeding Building Construction...")
    building_strands = [
        {
            "name": "1.0 Foundation of Building Construction",
            "substrands": [
                {
                    "name": "1.1 Introduction to Building Construction",
                    "assessment_methods": ["Observation schedule", "Checklist", "Written test"],
                    "slos": [
                        {"name": "Outline the functions of a building in day-to-day life", "description": "outline the functions of a building in day-to-day life", "assessment": "Observation schedule, Checklist, Written test"},
                        {"name": "Explain the historical development of buildings through ages", "description": "explain the historical development of buildings through ages"},
                        {"name": "Illustrate the basic components of a building to detail", "description": "illustrate the basic components of a building to detail"},
                        {"name": "Categorise buildings based on their use", "description": "categorise buildings based on their use"},
                        {"name": "Appreciate the importance of buildings in the locality", "description": "appreciate the importance of buildings in the locality"}
                    ]
                },
                {
                    "name": "1.2 Site Preparation",
                    "assessment_methods": ["Observation schedule", "Checklist", "Written test", "Rubrics", "Project", "Practical work"],
                    "slos": [
                        {"name": "Explain factors to consider when selecting a site for a given building", "description": "explain factors to consider when selecting a site for a given building"},
                        {"name": "Describe the safety measures to observe in site preparation", "description": "describe the safety measures to observe in site preparation"},
                        {"name": "Clear a site for construction using appropriate hand tools", "description": "clear a site for construction using appropriate hand tools"},
                        {"name": "Strip off the top soil of a building site", "description": "strip off the top soil of a building site"},
                        {"name": "Illustrate methods of levelling a site for building construction", "description": "illustrate methods of levelling a site for building construction"},
                        {"name": "Appreciate the importance of proper site selection and preparation before construction of a building", "description": "appreciate the importance of proper site selection and preparation before construction of a building"}
                    ]
                }
            ]
        },
        {
            "name": "2.0 Related Drawing",
            "substrands": [
                {
                    "name": "2.1 Isometric Drawing",
                    "assessment_methods": ["Observation schedule", "Checklist", "Written test", "Rubrics", "Project", "Practical work", "Portfolio"],
                    "slos": [
                        {"name": "Explain the characteristics of isometric drawings", "description": "explain the characteristics of isometric drawings"},
                        {"name": "Draw a shaped block in isometric projection", "description": "draw a shaped block in isometric projection"},
                        {"name": "Dimension shaped blocks drawn in isometric projection", "description": "dimension shaped blocks drawn in isometric projection"},
                        {"name": "Appreciate the importance of isometric projection in construction", "description": "appreciate the importance of isometric projection in construction"}
                    ]
                },
                {
                    "name": "2.2 Computer Aided Drawing",
                    "assessment_methods": ["Projects", "Portfolios", "Oral questions", "Aural questions", "Written tests", "Observation schedules", "Checklists"],
                    "slos": [
                        {"name": "Identify types of CAD software used in building drawing", "description": "identify types of CAD software used in building drawing"},
                        {"name": "Set up a CAD drawing environment on a digital device", "description": "set up a CAD drawing environment on a digital device"},
                        {"name": "Draw plane shapes using CAD software", "description": "draw plane shapes using CAD software"},
                        {"name": "Appreciate the importance of CAD in building drawing", "description": "appreciate the importance of CAD in building drawing"}
                    ]
                }
            ]
        },
        {
            "name": "3.0 Building Construction Processes",
            "substrands": [
                {
                    "name": "3.1 Concreting",
                    "assessment_methods": ["Observation schedule", "Checklist", "Written test", "Rubrics", "Project", "Practical work"],
                    "slos": [
                        {"name": "Explain the constituent materials for concrete", "description": "explain the constituent materials for concrete"},
                        {"name": "Select hand tools and equipment used for concrete production", "description": "select hand tools and equipment used for concrete production"},
                        {"name": "Describe the process of producing concrete", "description": "describe the process of producing concrete"},
                        {"name": "Perform the tasks for producing concrete", "description": "perform the tasks for producing concrete"},
                        {"name": "Appreciate the importance of concreting in building construction", "description": "appreciate the importance of concreting in building construction"}
                    ]
                },
                {
                    "name": "3.2 Foundations",
                    "assessment_methods": ["Checklist", "Observation schedule", "Written test", "Project", "Practical work", "Rubrics"],
                    "slos": [
                        {"name": "Describe types of foundations used in building construction", "description": "describe types of foundations used in building construction"},
                        {"name": "Set out a strip foundation from working drawings", "description": "set out a strip foundation from working drawings"},
                        {"name": "Prepare trenches for construction of a strip foundation", "description": "prepare trenches for construction of a strip foundation"},
                        {"name": "Lay a strip foundation for a building", "description": "lay a strip foundation for a building"},
                        {"name": "Acknowledge the importance of foundations in a building", "description": "acknowledge the importance of foundations in a building"}
                    ]
                },
                {
                    "name": "3.3 Timbering",
                    "assessment_methods": ["Checklist", "Oral tests", "Written test", "Observation", "Project", "Practical work", "Rubrics"],
                    "slos": [
                        {"name": "Identify materials for timbering", "description": "identify materials for timbering"},
                        {"name": "Describe the use of different types of timbering", "description": "describe the use of different types of timbering"},
                        {"name": "Illustrate timbering methods for different soils", "description": "illustrate timbering methods for different soils"},
                        {"name": "Perform timbering to a foundation trench", "description": "perform timbering to a foundation trench"},
                        {"name": "Value the importance of timbering to foundation trenches", "description": "value the importance of timbering to foundation trenches"}
                    ]
                },
                {
                    "name": "3.4 Foundation Walling",
                    "assessment_methods": ["Checklist", "Oral tests", "Written test", "Project", "Practical work", "Rubrics"],
                    "slos": [
                        {"name": "Select materials for foundation walling", "description": "select materials for foundation walling"},
                        {"name": "Set out a foundation wall from profile boards", "description": "set out a foundation wall from profile boards"},
                        {"name": "Construct a masonry foundation wall in a given bond", "description": "construct a masonry foundation wall in a given bond"},
                        {"name": "Appreciate the importance of foundation walls in a building", "description": "appreciate the importance of foundation walls in a building"}
                    ]
                },
                {
                    "name": "3.5 Ground Floors",
                    "assessment_methods": ["Checklist", "Oral tests", "Observation", "Written test", "Practical work", "Rubrics"],
                    "slos": [
                        {"name": "Identify types of ground floors used in buildings", "description": "identify types of ground floors used in buildings"},
                        {"name": "Illustrate the components of a solid ground floor", "description": "illustrate the components of a solid ground floor"},
                        {"name": "Construct a solid ground floor for a building", "description": "construct a solid ground floor for a building"},
                        {"name": "Appreciate the importance of solid ground floors in a building", "description": "appreciate the importance of solid ground floors in a building"}
                    ]
                }
            ]
        },
        {
            "name": "4.0 Building Services",
            "substrands": [
                {
                    "name": "4.1 Plumbing Tools and Equipment",
                    "assessment_methods": ["Oral tests", "Observation", "Checklist", "Written test", "Rubrics", "Project", "Practical work"],
                    "slos": [
                        {"name": "Identify tools and equipment for plumbing works", "description": "identify tools and equipment for plumbing works"},
                        {"name": "Explain the safety measures to observe when handling plumbing tools and equipment", "description": "explain the safety measures to observe when handling plumbing tools and equipment"},
                        {"name": "Use plumbing tools and equipment to perform a given task", "description": "use plumbing tools and equipment to perform a given task"},
                        {"name": "Maintain plumbing tools and equipment at the workplace", "description": "maintain plumbing tools and equipment at the workplace"},
                        {"name": "Appreciate the importance of tools and equipment in plumbing", "description": "appreciate the importance of tools and equipment in plumbing"}
                    ]
                },
                {
                    "name": "4.2 Plumbing Materials",
                    "assessment_methods": ["Oral tests", "Observation", "Checklist", "Written test", "Rubrics", "Project", "Practical work"],
                    "slos": [
                        {"name": "Identify materials used in plumbing", "description": "identify materials used in plumbing"},
                        {"name": "Describe the properties of materials used in plumbing", "description": "describe the properties of materials used in plumbing"},
                        {"name": "Select materials for specified plumbing use", "description": "select materials for specified plumbing use"},
                        {"name": "Recognise importance of materials used in plumbing", "description": "recognise importance of materials used in plumbing"}
                    ]
                },
                {
                    "name": "4.3 Pipework",
                    "assessment_methods": ["Portfolio", "Observation", "Interview"],
                    "slos": [
                        {"name": "Identify types of pipes and fittings used in plumbing", "description": "identify types of pipes and fittings used in plumbing"},
                        {"name": "Prepare pipe joints in plumbing", "description": "prepare pipe joints in plumbing"},
                        {"name": "Perform pipe bending in plumbing", "description": "perform pipe bending in plumbing"},
                        {"name": "Observe safety when performing pipework", "description": "observe safety when performing pipework"},
                        {"name": "Appreciate the importance of proper pipework in plumbing", "description": "appreciate the importance of proper pipework in plumbing"}
                    ]
                }
            ]
        }
    ]
    await seed_subject("Building Construction", building_strands)

    # ============================================================
    # BUSINESS STUDIES
    # ============================================================
    print("\nSeeding Business Studies...")
    business_strands = [
        {
            "name": "1.0 Business and Money Management",
            "substrands": [
                {
                    "name": "1.1 Money",
                    "assessment_methods": ["Written test", "Oral questions", "Discussions", "Quizzes", "Project"],
                    "slos": [
                        {"name": "Identify the key security features of the Kenyan currency", "description": "identify the key security features of the Kenyan currency", "assessment": "Exceeds: Describes five functions of money citing examples. Meets: Describes five functions. Approaches: Describes three to four functions. Below: Describes less than three functions."},
                        {"name": "Describe the functions of money when carrying out financial transactions", "description": "describe the functions of money when carrying out financial transactions"},
                        {"name": "Justify the demand for money for achieving economic development", "description": "justify the demand for money for achieving economic development"},
                        {"name": "Examine the factors that determine supply of money in an economy", "description": "examine the factors that determine supply of money in an economy"},
                        {"name": "Evaluate ethical practices on the use of money in financial transactions", "description": "evaluate ethical practices on the use of money in financial transactions"},
                        {"name": "Acknowledge the role of money in day-to-day life", "description": "acknowledge the role of money in day-to-day life"}
                    ]
                },
                {
                    "name": "1.2 Business Goals",
                    "assessment_methods": ["Written test", "Oral questions", "Discussions", "Quizzes", "Project"],
                    "slos": [
                        {"name": "Analyse the importance of goal setting in business", "description": "analyse the importance of goal setting in business", "assessment": "Exceeds: Formulates SMART goals citing examples. Meets: Formulates SMART short and long term goals. Approaches: Formulates goals missing one or two SMART elements. Below: With guidance, formulates goals."},
                        {"name": "Examine the factors to consider when setting goals for a business", "description": "examine the factors to consider when setting goals for a business"},
                        {"name": "Describe steps followed when setting business goals", "description": "describe steps followed when setting business goals"},
                        {"name": "Formulate SMART short term and long term goals for a business", "description": "formulate SMART short term and long term goals for a business"},
                        {"name": "Appreciate the need for setting goals in business", "description": "appreciate the need for setting goals in business"}
                    ]
                },
                {
                    "name": "1.3 Budgeting in Business",
                    "assessment_methods": ["Written test", "Oral questions", "Discussions", "Quizzes", "Project"],
                    "slos": [
                        {"name": "Explain the importance of budgeting in business", "description": "explain the importance of budgeting in business", "assessment": "Exceeds: Prepares a budget with all components giving budget notes. Meets: Prepares a budget to control spending. Approaches: Prepares a budget without factoring in contingencies. Below: With assistance, prepares a budget."},
                        {"name": "Analyse the types of business budgets for financial planning", "description": "analyse the types of business budgets for financial planning"},
                        {"name": "Prepare a budget to control spending in business", "description": "prepare a budget to control spending in business"},
                        {"name": "Appreciate the need for budgeting in business", "description": "appreciate the need for budgeting in business"}
                    ]
                },
                {
                    "name": "1.4 Banking",
                    "assessment_methods": ["Written test", "Oral questions", "Discussions", "Quizzes"],
                    "slos": [
                        {"name": "Explain the importance of banking in an economy", "description": "explain the importance of banking in an economy", "assessment": "Exceeds: Explains five importance of banking with examples. Meets: Explains five importance. Approaches: Explains three to four importance. Below: Explains less than three importance."},
                        {"name": "Analyse types of accounts offered by banks", "description": "analyse types of accounts offered by banks"},
                        {"name": "Explore the ethical practices in banking", "description": "explore the ethical practices in banking"},
                        {"name": "Describe the trends in banking in Kenya", "description": "describe the trends in banking in Kenya"},
                        {"name": "Appreciate the role of banking in an economy", "description": "appreciate the role of banking in an economy"}
                    ]
                }
            ]
        },
        {
            "name": "2.0 Business and Its Environment",
            "substrands": [
                {
                    "name": "2.1 Business Activities",
                    "assessment_methods": ["Written test", "Oral questions", "Discussions", "Quizzes", "Project"],
                    "slos": [
                        {"name": "Explain the concept of needs and wants as used in day to day life", "description": "explain the concept of needs and wants as used in day to day life", "assessment": "Exceeds: Analyses three types of economic resources giving examples. Meets: Analyses three types. Approaches: Analyses two types. Below: Analyses less than two types."},
                        {"name": "Analyse the types of economic resources in satisfaction of human needs and wants", "description": "analyse the types of economic resources in satisfaction of human needs and wants"},
                        {"name": "Investigate the importance of business activities in the society", "description": "investigate the importance of business activities in the society"},
                        {"name": "Classify business activities in an economy", "description": "classify business activities in an economy"},
                        {"name": "Examine the micro and macro factors that affect business activities", "description": "examine the micro and macro factors that affect business activities"},
                        {"name": "Appreciate the importance of business activities in an economy", "description": "appreciate the importance of business activities in an economy"}
                    ]
                },
                {
                    "name": "2.2 Types of Business Ownership",
                    "assessment_methods": ["Written test", "Oral questions", "Discussions", "Quizzes", "Project"],
                    "slos": [
                        {"name": "Explore the formation, management, sources of finance, advantages, and disadvantages of a sole proprietorship", "description": "explore the formation, management, sources of finance, advantages, and disadvantages of a sole proprietorship business enterprise in Kenya", "assessment": "Exceeds: Explains five advantages of sole proprietorship with examples. Meets: Explains five advantages. Approaches: Explains three to four advantages. Below: Explains less than three advantages."},
                        {"name": "Examine the formation, management, sources of finance, advantages, and disadvantages of a partnership", "description": "examine the formation, management, sources of finance, advantages, and disadvantages of a partnership business enterprise in Kenya"},
                        {"name": "Analyse the formation, types, management, sources of finance, advantages, and disadvantages of a cooperative", "description": "analyse the formation, types, management, sources of finance, advantages, and disadvantages of a cooperative for economic growth"},
                        {"name": "Acknowledge the role of sole proprietorship, partnerships and cooperative societies in the economy", "description": "acknowledge the role of sole proprietorship, partnerships and cooperative societies in the economy"}
                    ]
                },
                {
                    "name": "2.3 Social Responsibility of Business",
                    "assessment_methods": ["Written test", "Oral questions", "Discussions", "Quizzes", "Project"],
                    "slos": [
                        {"name": "Justify the need for social responsibility of a business in the society", "description": "justify the need for social responsibility of a business in the society", "assessment": "Exceeds: Justifies five needs for social responsibility giving examples. Meets: Justifies five needs. Approaches: Justifies three to four needs. Below: Justifies less than three needs."},
                        {"name": "Examine social responsibility activities of a business in the community", "description": "examine social responsibility activities of a business in the community"},
                        {"name": "Analyse the challenges faced by businesses when carrying out social responsibilities", "description": "analyse the challenges faced by businesses when carrying out social responsibilities"},
                        {"name": "Design and implement a social responsibility activity in the school", "description": "design and implement a social responsibility activity in the school"},
                        {"name": "Appreciate the need for business social responsibility in the society and the environment", "description": "appreciate the need for business social responsibility in the society and the environment"}
                    ]
                },
                {
                    "name": "2.4 Entrepreneurship",
                    "assessment_methods": ["Written test", "Oral questions", "Discussions", "Quizzes", "Project"],
                    "slos": [
                        {"name": "Assess the entrepreneurial skills for economic growth", "description": "assess the entrepreneurial skills for economic growth", "assessment": "Exceeds: Assesses five entrepreneurial skills giving examples. Meets: Assesses five skills. Approaches: Assesses three to four skills. Below: Assesses less than three skills."},
                        {"name": "Examine the types of entrepreneurs in business", "description": "examine the types of entrepreneurs in business"},
                        {"name": "Evaluate business ideas and opportunities for business start-ups", "description": "evaluate business ideas and opportunities for business start-ups"},
                        {"name": "Justify the importance of incubation for business growth", "description": "justify the importance of incubation for business growth"},
                        {"name": "Identify an opportunity and start a business in school", "description": "identify an opportunity and start a business in school"},
                        {"name": "Embrace entrepreneurial skills in business start-ups", "description": "embrace entrepreneurial skills in business start-ups"}
                    ]
                },
                {
                    "name": "2.5 Production",
                    "assessment_methods": ["Written test", "Oral questions", "Discussions", "Quizzes", "Project"],
                    "slos": [
                        {"name": "Analyse the importance of production in an economy", "description": "analyse the importance of production in an economy", "assessment": "Exceeds: Analyses five importance of production giving examples. Meets: Analyses five importance. Approaches: Analyses three to four importance. Below: Analyses less than three importance."},
                        {"name": "Explain factors of production required to produce goods and services", "description": "explain factors of production required to produce goods and services"},
                        {"name": "Determine the types of costs in a production unit", "description": "determine the types of costs in a production unit"},
                        {"name": "Analyse the concept of the division of labour and specialization in production", "description": "analyse the concept of the division of labour and specialization in production"},
                        {"name": "Examine the roles and responsibilities of a producer to consumer", "description": "examine the roles and responsibilities of a producer to consumer"},
                        {"name": "Design an appropriate label for a product", "description": "design an appropriate label for a product"},
                        {"name": "Recognize the role of production in an economy", "description": "recognize the role of production in an economy"}
                    ]
                },
                {
                    "name": "2.6 Consumer Satisfaction",
                    "assessment_methods": ["Written test", "Oral questions", "Discussions", "Quizzes", "Survey"],
                    "slos": [
                        {"name": "Explore the importance of consumer satisfaction in business", "description": "explore the importance of consumer satisfaction in business", "assessment": "Exceeds: Explores five importance citing examples. Meets: Explores five importance. Approaches: Explores three to four importance. Below: Explores less than three importance."},
                        {"name": "Examine the terms and conditions for the supply of goods and services to a consumer", "description": "examine the terms and conditions for the supply of goods and services to a consumer"},
                        {"name": "Justify the remedies for consumer satisfaction", "description": "justify the remedies for consumer satisfaction"},
                        {"name": "Carry out a customer satisfaction survey for improvement of service delivery", "description": "carry out a customer satisfaction survey for improvement of service delivery"},
                        {"name": "Embrace the importance of customer satisfaction for business sustainability", "description": "embrace the importance of customer satisfaction for business sustainability"}
                    ]
                }
            ]
        },
        {
            "name": "3.0 Government and Global Influence in Business",
            "substrands": [
                {
                    "name": "3.1 Public Finance",
                    "assessment_methods": ["Written test", "Oral questions", "Discussions", "Quizzes", "Article writing"],
                    "slos": [
                        {"name": "Explain the importance of public finance in Kenya", "description": "explain the importance of public finance in Kenya", "assessment": "Exceeds: Discusses requirements for tax compliance citing examples. Meets: Discusses the requirements. Approaches: Discusses two requirements. Below: Discusses less than two requirements."},
                        {"name": "Assess the concept of taxation in Kenya", "description": "assess the concept of taxation in Kenya"},
                        {"name": "Analyse the types of custom duties in Kenya", "description": "analyse the types of custom duties in Kenya"},
                        {"name": "Evaluate the trends in taxation in Kenya", "description": "evaluate the trends in taxation in Kenya"},
                        {"name": "Identify ethical issues in taxation", "description": "identify ethical issues in taxation"},
                        {"name": "Write an article on importance of taxation in Kenya to sensitize the community", "description": "write an article on importance of taxation in Kenya to sensitize the community"},
                        {"name": "Appreciate the role of public finance in Kenya", "description": "appreciate the role of public finance in Kenya"}
                    ]
                },
                {
                    "name": "3.2 International Trade",
                    "assessment_methods": ["Written test", "Oral questions", "Discussions", "Quizzes", "Project", "Mapping"],
                    "slos": [
                        {"name": "Examine the concept of international trade in an economy", "description": "examine the concept of international trade in an economy", "assessment": "Exceeds: Analyses five transaction documents with illustrations. Meets: Analyses five transaction documents. Approaches: Analyses three to four documents. Below: Analyses less than three documents."},
                        {"name": "Explore the limitations of international trade to a country", "description": "explore the limitations of international trade to a country"},
                        {"name": "Analyse the terms of sale and payments used in international trade", "description": "analyse the terms of sale and payments used in international trade"},
                        {"name": "Explore digital applications in international trade", "description": "explore digital applications in international trade"},
                        {"name": "Map the local products that can be developed for export", "description": "map the local products that can be developed for export"},
                        {"name": "Appreciate the importance of international trade in an economy", "description": "appreciate the importance of international trade in an economy"}
                    ]
                }
            ]
        },
        {
            "name": "4.0 Financial Records in Business",
            "substrands": [
                {
                    "name": "4.1 Business Transactions",
                    "assessment_methods": ["Written test", "Oral questions", "Discussions", "Quizzes", "Survey"],
                    "slos": [
                        {"name": "Explain the concept of business transaction in book keeping", "description": "explain the concept of business transaction in book keeping", "assessment": "Exceeds: Analyses five payment methods giving examples. Meets: Analyses five methods. Approaches: Analyses three to four methods. Below: Analyses less than three methods."},
                        {"name": "Analyse methods used in making payments for goods and services", "description": "analyse methods used in making payments for goods and services"},
                        {"name": "Carry out a survey on the methods of payment in the school", "description": "carry out a survey on the methods of payment in the school"},
                        {"name": "Recognize the methods of making payments for goods and services", "description": "recognize the methods of making payments for goods and services"}
                    ]
                },
                {
                    "name": "4.2 Effects of Business Transactions",
                    "assessment_methods": ["Written test", "Oral questions", "Discussions", "Quizzes"],
                    "slos": [
                        {"name": "Analyse the effects of business transactions on the statement of financial position", "description": "analyse the effects of business transactions on the statement of financial position for a business", "assessment": "Exceeds: Prepares statement in order of permanency or liquidity. Meets: Prepares a statement of financial position. Approaches: Prepares missing one component. Below: With assistance, prepares the statement."},
                        {"name": "Prepare a statement of financial position after adjustments to determine net worth", "description": "prepare a statement of financial position after adjustments to determine the net worth of a business"},
                        {"name": "Recognise the effects of transactions when determining the net worth of a business", "description": "recognise the effects of transactions when determining the net worth of a business"}
                    ]
                },
                {
                    "name": "4.3 Source Documents and Books of Original Entry",
                    "assessment_methods": ["Written test", "Oral questions", "Discussions", "Quizzes", "Practical work"],
                    "slos": [
                        {"name": "Explain the importance of source documents and books of original entry in book keeping", "description": "explain the importance of source documents and books of original entry in book keeping", "assessment": "Exceeds: Records in five books and posts in relevant ledger accounts. Meets: Records in five relevant books. Approaches: Records in three to four books. Below: With assistance, records in less than three books."},
                        {"name": "Analyse the source documents used for recording business transactions", "description": "analyse the source documents used for recording business transactions"},
                        {"name": "Examine the books of original entry used in book keeping", "description": "examine the books of original entry used in book keeping"},
                        {"name": "Record transactions in the relevant books of original entry", "description": "record transactions in the relevant books of original entry"},
                        {"name": "Appreciate the books of original entry for recording business transactions", "description": "appreciate the books of original entry for recording business transactions"}
                    ]
                }
            ]
        }
    ]
    await seed_subject("Business Studies", business_strands)

    # ============================================================
    # CHEMISTRY
    # ============================================================
    print("\nSeeding Chemistry...")
    chemistry_strands = [
        {
            "name": "1.0 Inorganic Chemistry",
            "substrands": [
                {
                    "name": "1.1 Introduction to Chemistry",
                    "assessment_methods": ["Discussions", "Observations", "Quizzes", "Posters", "Presentations"],
                    "slos": [
                        {"name": "Explain the meaning of Chemistry as a field of science", "description": "explain the meaning of Chemistry as a field of science", "assessment": "Communication and Collaboration: Explores teamwork with peers. Self-efficacy: Effectively communicates findings on career opportunities. Digital literacy: Uses digital technology to search for information. Citizenship: Demonstrates critical dialogue on consumer rights."},
                        {"name": "Explore the role of Chemistry in day to day life", "description": "explore the role of Chemistry in day to day life"},
                        {"name": "Examine the effects of drug and substance use in day to day life", "description": "examine the effects of drug and substance use in day to day life"},
                        {"name": "Promote the rights and responsibilities to a safe and healthy learning environment", "description": "promote the rights and responsibilities to a safe and healthy learning environment"}
                    ]
                },
                {
                    "name": "1.2 The Atom",
                    "assessment_methods": ["Discussions", "Observations", "Quizzes", "Written test", "Practical work", "Models"],
                    "slos": [
                        {"name": "Describe the structure of the atom", "description": "describe the structure of the atom", "assessment": "Digital literacy: Uses digital platforms for animations on atomic models. Creativity and Imagination: Experiments with ideas while modelling the atom. Learning to learn: Reflects on own work practising electron arrangements."},
                        {"name": "Determine the relative atomic mass of elements", "description": "determine the relative atomic mass of elements"},
                        {"name": "Write the electron arrangement of elements using s and p notation", "description": "write the electron arrangement of elements using s and p notation"},
                        {"name": "Develop interest in the study of structure of the atom", "description": "develop interest in the study of structure of the atom"}
                    ]
                },
                {
                    "name": "1.3 The Periodic Table",
                    "assessment_methods": ["Discussions", "Written test", "Quizzes", "Practical work"],
                    "slos": [
                        {"name": "Relate the position of an element in the periodic table to its electron arrangement", "description": "relate the position of an element in the periodic table to its electron arrangement", "assessment": "Communication and Collaboration: Listens keenly while discussing relationships. Critical thinking: Creates new ideas while drawing ion diagrams. Learning to learn: Independently writes balanced equations."},
                        {"name": "Illustrate ion formation of elements", "description": "illustrate ion formation of elements"},
                        {"name": "Derive the formulae of compounds", "description": "derive the formulae of compounds"},
                        {"name": "Write balanced equations for chemical reactions", "description": "write balanced equations for chemical reactions"},
                        {"name": "Appreciate the role of electron arrangement in the development of the periodic table", "description": "appreciate the role of electron arrangement in the development of the periodic table"}
                    ]
                },
                {
                    "name": "1.4 Chemical Bonding",
                    "assessment_methods": ["Discussions", "Written test", "Quizzes", "Practical work", "Experiments", "Models"],
                    "slos": [
                        {"name": "Illustrate bond types in elements, molecules and compounds", "description": "illustrate bond types in elements, molecules and compounds", "assessment": "Learning to learn: Independently draws dot and cross diagrams. Digital literacy: Uses digital technology for animations on bonding. Creativity and Imagination: Develops models to illustrate bonding. Critical Thinking: Interprets relationship between bond types and structures."},
                        {"name": "Investigate the relationship between bond types and physical properties", "description": "investigate the relationship between bond types and physical properties of elements, molecules and compounds"},
                        {"name": "Relate bond types and resultant structures to the uses of elements, molecules and compounds", "description": "relate bond types and resultant structures to the uses of elements, molecules and compounds"},
                        {"name": "Appreciate the uses of different substances based on their bond types and structures", "description": "appreciate the uses of different substances based on their bond types and structures in day to day life"}
                    ]
                },
                {
                    "name": "1.5 Periodicity",
                    "assessment_methods": ["Discussions", "Written test", "Quizzes", "Experiments", "Presentations", "Practical work"],
                    "slos": [
                        {"name": "Describe the trends in physical properties of elements of the periodic table", "description": "describe the trends in physical properties of elements of the periodic table", "assessment": "Communication and Collaboration: Discusses trends in physical properties. Self-efficacy: Confidently communicates uses of elements. Learning to learn: Independently practises writing balanced equations. Digital literacy: Uses devices to search for element uses."},
                        {"name": "Investigate the chemical properties of elements in group of the periodic table", "description": "investigate the chemical properties of elements in group of the periodic table"},
                        {"name": "Describe the trends in properties across a period", "description": "describe the trends in properties across a period"},
                        {"name": "Outline applications of elements of the periodic table", "description": "outline applications of elements of the periodic table"},
                        {"name": "Appreciate applications of various elements of the periodic table", "description": "appreciate applications of various elements of the periodic table"}
                    ]
                }
            ]
        },
        {
            "name": "2.0 Physical Chemistry",
            "substrands": [
                {
                    "name": "2.1 Acids and Bases",
                    "assessment_methods": ["Discussions", "Written test", "Experiments", "Practical work", "Observations"],
                    "slos": [
                        {"name": "Explain the characteristics of acids and bases in aqueous solutions", "description": "explain the characteristics of acids and bases in aqueous solutions", "assessment": "Communication and Collaboration: Develops teamwork through group experiments. Digital literacy: Searches for information on applications of acids and bases."},
                        {"name": "Describe the chemical properties of acids and bases", "description": "describe the chemical properties of acids and bases"},
                        {"name": "Classify acids and bases into strong and weak using universal indicator", "description": "classify acids and bases into strong and weak using universal indicator"},
                        {"name": "Outline the uses of acids and bases in day to day life", "description": "outline the uses of acids and bases in day to day life"},
                        {"name": "Appreciate the uses of acids and bases in day to day activities", "description": "appreciate the uses of acids and bases in day to day activities"}
                    ]
                },
                {
                    "name": "2.2 Introduction to Salts",
                    "assessment_methods": ["Discussions", "Written test", "Experiments", "Practical work", "Presentations"],
                    "slos": [
                        {"name": "Classify different salts based on their properties", "description": "classify different salts based on their properties", "assessment": "Communication and Collaboration: Brainstorms with peers to establish meaning of salt. Learning to learn: Shares what learnt while preparing salts. Creativity and imagination: Makes observations determining solubility of salts."},
                        {"name": "Prepare salts using appropriate methods in the laboratory", "description": "prepare salts using appropriate methods in the laboratory"},
                        {"name": "Describe the behaviour of salts when exposed to air", "description": "describe the behaviour of salts when exposed to air"},
                        {"name": "Outline applications of salts in day to day life", "description": "outline applications of salts in day to day life"},
                        {"name": "Appreciate applications of salts in day to day life", "description": "appreciate applications of salts in day to day life"}
                    ]
                }
            ]
        }
    ]
    await seed_subject("Chemistry", chemistry_strands)

    # --- SUMMARY ---
    total_grades = await db.grades.count_documents({})
    total_subjects = await db.subjects.count_documents({})
    total_strands = await db.strands.count_documents({})
    total_substrands = await db.substrands.count_documents({})
    total_slos = await db.slos.count_documents({})
    total_mappings = await db.slo_mappings.count_documents({})
    total_assessments = await db.assessments.count_documents({})
    total_la = await db.learning_activities.count_documents({})

    print(f"\n=== SEEDING COMPLETE ===")
    print(f"Grades: {total_grades}")
    print(f"Subjects: {total_subjects}")
    print(f"Strands: {total_strands}")
    print(f"Sub-strands: {total_substrands}")
    print(f"SLOs: {total_slos}")
    print(f"SLO Mappings: {total_mappings}")
    print(f"Assessments: {total_assessments}")
    print(f"Learning Activities: {total_la}")

    client.close()

asyncio.run(seed())
