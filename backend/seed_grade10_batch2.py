"""
Seed Grade 10 Batch 2 subjects from PDF extractions.
Subjects: Biology, CRE, Electrical Technology, English, Fasihi ya Kiswahili
Replaces any existing data for these subjects.
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'cbeplanner')

async def seed():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    print(f"Connected to DB: {DB_NAME}")

    # Get or create Grade 10
    grade = await db.grades.find_one({"name": "Grade 10"})
    if not grade:
        result = await db.grades.insert_one({"name": "Grade 10", "order": 10})
        grade_id = str(result.inserted_id)
    else:
        grade_id = str(grade["_id"])
    print(f"Grade 10: {grade_id}")

    # Cache competencies, values, PCIs
    comp_ids = []
    for n in ["Communication and Collaboration", "Critical Thinking and Problem Solving", "Learning to Learn"]:
        c = await db.competencies.find_one({"name": n})
        if c: comp_ids.append(str(c["_id"]))
    val_ids = []
    for n in ["Responsibility", "Respect", "Integrity"]:
        v = await db.values.find_one({"name": n})
        if v: val_ids.append(str(v["_id"]))
    pci_ids = []
    for n in ["Life Skills", "Citizenship"]:
        p = await db.pcis.find_one({"name": n})
        if p: pci_ids.append(str(p["_id"]))
    print(f"Cached: {len(comp_ids)} competencies, {len(val_ids)} values, {len(pci_ids)} PCIs")

    async def clear_subject(name):
        old = await db.subjects.find_one({"name": name, "gradeIds": grade_id})
        if not old:
            return
        sid = str(old["_id"])
        strands = await db.strands.find({"subjectId": sid}).to_list(500)
        for st in strands:
            subs = await db.substrands.find({"strandId": str(st["_id"])}).to_list(500)
            for ss in subs:
                ssid = str(ss["_id"])
                slos = await db.slos.find({"substrandId": ssid}).to_list(500)
                for slo in slos:
                    await db.slo_mappings.delete_many({"sloId": str(slo["_id"])})
                await db.slos.delete_many({"substrandId": ssid})
                await db.learning_activities.delete_many({"substrandId": ssid})
            await db.substrands.delete_many({"strandId": str(st["_id"])})
        await db.strands.delete_many({"subjectId": sid})
        remaining = [g for g in old.get("gradeIds", []) if g != grade_id]
        if remaining:
            await db.subjects.update_one({"_id": old["_id"]}, {"$set": {"gradeIds": remaining}})
        else:
            await db.subjects.delete_one({"_id": old["_id"]})
        print(f"  Cleared old {name}")

    async def create_mapping(slo_id, assessment_text=""):
        assessment_ids = []
        if assessment_text:
            a = await db.assessments.insert_one({"name": "Suggested Evaluation", "description": assessment_text})
            assessment_ids.append(str(a.inserted_id))
        await db.slo_mappings.insert_one({
            "sloId": slo_id,
            "competencyIds": comp_ids,
            "valueIds": val_ids,
            "pciIds": pci_ids,
            "assessmentIds": assessment_ids
        })

    async def seed_subject(name, strands_data):
        await clear_subject(name)
        existing = await db.subjects.find_one({"name": name})
        if existing:
            await db.subjects.update_one({"_id": existing["_id"]}, {"$addToSet": {"gradeIds": grade_id}})
            subject_id = str(existing["_id"])
        else:
            result = await db.subjects.insert_one({"name": name, "gradeIds": [grade_id]})
            subject_id = str(result.inserted_id)

        slo_count = 0
        for s_idx, strand in enumerate(strands_data):
            sr = await db.strands.insert_one({"name": strand["name"], "subjectId": subject_id, "order": s_idx + 1})
            strand_id = str(sr.inserted_id)
            for ss_idx, ss in enumerate(strand["substrands"]):
                ssr = await db.substrands.insert_one({"name": ss["name"], "strandId": strand_id, "order": ss_idx + 1})
                ss_id = str(ssr.inserted_id)
                if ss.get("assessment_methods"):
                    await db.learning_activities.insert_one({
                        "substrandId": ss_id,
                        "introduction_activities": [], "development_activities": [],
                        "conclusion_activities": [], "extended_activities": [],
                        "learning_resources": [], "assessment_methods": ss["assessment_methods"]
                    })
                for slo_idx, slo in enumerate(ss["slos"]):
                    slor = await db.slos.insert_one({
                        "name": slo["name"], "description": slo.get("description", ""),
                        "substrandId": ss_id, "order": slo_idx + 1
                    })
                    await create_mapping(str(slor.inserted_id), slo.get("assessment", ""))
                    slo_count += 1
        print(f"  {name}: {len(strands_data)} strands, {slo_count} SLOs")
        return subject_id

    # ============================================================
    # BIOLOGY - 3 strands, 9 substrands
    # ============================================================
    print("\nSeeding Biology...")
    biology = [
        {"name": "1.0 Cell Biology and Biodiversity", "substrands": [
            {"name": "1.1 Introduction to Biology", "assessment_methods": ["Discussions", "Presentations", "Career wheels", "Flashcards"], "slos": [
                {"name": "Explain the application of Biology in everyday life", "description": "explain the application of Biology in everyday life",
                 "assessment": "Exceeds: Correctly and precisely relates all fields of study in Biology to the respective career opportunities. Meets: Correctly relates all fields of study in Biology to career opportunities. Approaches: Relates most fields of study in Biology to career opportunities. Below: Relates a few fields of study in Biology to career opportunities."},
                {"name": "Relate fields of study in Biology to career opportunities", "description": "relate fields of study in Biology to career opportunities"},
                {"name": "Illustrate the careers related to fields of study in Biology", "description": "illustrate the careers related to fields of study in Biology"},
                {"name": "Appreciate the importance of Biology in everyday life", "description": "appreciate the importance of Biology in everyday life"}
            ]},
            {"name": "1.2 Specimen Collection and Preservation", "assessment_methods": ["Project work", "Portfolio", "Observation", "Peer assessment"], "slos": [
                {"name": "Identify apparatus and materials used for collecting, processing and preserving specimens", "description": "identify apparatus and materials used for collecting, processing and preserving specimens",
                 "assessment": "Exceeds: Procedurally collects, sorts, processes and preserves specimens using improvised and conventional apparatus. Meets: Procedurally collects, processes and preserves specimens using improvised and conventional apparatus. Approaches: Collects, processes and preserves specimens using conventional apparatus only. Below: Collects and processes but fails to preserve specimens."},
                {"name": "Collect, process and preserve specimens for biological studies using improvised and conventional apparatus", "description": "collect, process and preserve specimens for biological studies"},
                {"name": "Appreciate the importance of collecting, processing and preserving specimens in Biology", "description": "appreciate the importance of collecting, processing and preserving specimens in Biology"}
            ]},
            {"name": "1.3 Cell Structure and Specialization", "assessment_methods": ["Practical work", "Drawing and labeling", "Modeling", "Discussions", "Peer assessment"], "slos": [
                {"name": "Differentiate between light and electron microscope as used in the study of cell structure", "description": "differentiate between light and electron microscope as used in the study of cell structure",
                 "assessment": "Exceeds: Coherently describes the structure and functions of plant and animal cells as seen under electron microscope. Meets: Describes the structure and functions of plant and animal cells as seen under electron microscope. Approaches: Partly describes the structure and functions. Below: Incoherently describes the structure and functions."},
                {"name": "Describe the structure and functions of plant and animal cells as observed in an electron microscope", "description": "describe the structure and functions of plant and animal cells as observed in an electron microscope"},
                {"name": "Prepare temporary slides for observation and estimation of cell size using a light microscope", "description": "prepare temporary slides for observation and estimation of cell size using a light microscope"},
                {"name": "Relate the structures of specialized cells in plants and animals to their functions", "description": "relate the structures of specialized cells in plants and animals to their functions"},
                {"name": "Appreciate the cell as the basic unit of life", "description": "appreciate the cell as the basic unit of life"}
            ]},
            {"name": "1.4 Chemicals of Life", "assessment_methods": ["Experiments", "Analysis", "Food label examination", "Discussions"], "slos": [
                {"name": "Describe the composition, properties and functions of the chemicals of life in organisms", "description": "describe the composition, properties and functions of the chemicals of life in organisms",
                 "assessment": "Exceeds: Correctly describes the composition, properties and functions of all chemicals of life with appropriate illustrations. Meets: Correctly describes the composition, properties and functions of all chemicals of life. Approaches: Describes the composition, properties and functions of most of the chemicals of life. Below: Describes the composition, properties and functions of a few of the chemicals of life."},
                {"name": "Investigate the presence of carbohydrates, lipids, proteins and vitamin C in food substances", "description": "investigate the presence of carbohydrates, lipids, proteins and vitamin C in food substances"},
                {"name": "Investigate the presence of enzymes in living tissues", "description": "investigate the presence of enzymes in living tissues"},
                {"name": "Determine factors affecting enzymatic reactions in cells", "description": "determine factors affecting enzymatic reactions in cells"},
                {"name": "Appreciate the importance of chemical components in cells", "description": "appreciate the importance of chemical components in cells"}
            ]}
        ]},
        {"name": "2.0 Anatomy and Physiology of Plants", "substrands": [
            {"name": "2.1 Nutrition", "assessment_methods": ["Discussions", "Presentations", "Observation"], "slos": [
                {"name": "Describe types of nutrition in plants", "description": "describe types of nutrition in plants",
                 "assessment": "Exceeds: Accurately illustrates the light and dark stages of photosynthesis. Meets: Illustrates the light and dark stages of photosynthesis. Approaches: Partly illustrates the light and dark stages. Below: Partly illustrates with prompts."},
                {"name": "Relate the structure of the chloroplast to its function in plant cells", "description": "relate the structure of the chloroplast to its function in plant cells"},
                {"name": "Illustrate the light and dark stages of photosynthesis in plants", "description": "illustrate the light and dark stages of photosynthesis in plants"},
                {"name": "Appreciate the significance of photosynthesis in nature", "description": "appreciate the significance of photosynthesis in nature"}
            ]},
            {"name": "2.2 Transport", "assessment_methods": ["Microscopy", "Experiments", "Discussions", "Drawing"], "slos": [
                {"name": "Relate structures of the plant transport system to their functions in plants", "description": "relate structures of the plant transport system to their functions in plants",
                 "assessment": "Exceeds: Comprehensively relates the structures of the plant transport system to their functions. Meets: Relates the structures of the plant transport system to their functions. Approaches: Relates some structures to their functions. Below: Relates some structures to their functions with difficulty."},
                {"name": "Illustrate the arrangement of vascular tissues in monocotyledonous and dicotyledonous plants", "description": "illustrate the arrangement of vascular tissues in monocotyledonous and dicotyledonous plants"},
                {"name": "Demonstrate the uptake of water and mineral salts from the roots to the leaves", "description": "demonstrate the uptake of water and mineral salts from the roots to the leaves"},
                {"name": "Demonstrate factors that affect the rate of transpiration in plants", "description": "demonstrate factors that affect the rate of transpiration in plants"},
                {"name": "Describe the translocation of manufactured food in plants", "description": "describe the translocation of manufactured food in plants"},
                {"name": "Appreciate the significance of transport in plants", "description": "appreciate the significance of transport in plants"}
            ]},
            {"name": "2.3 Gaseous Exchange and Respiration", "assessment_methods": ["Observation", "Experiments", "Project work", "Discussions"], "slos": [
                {"name": "Relate the structure of gaseous exchange sites in plants to their function", "description": "relate the structure of gaseous exchange sites in plants to their function",
                 "assessment": "Exceeds: Correctly describes the economic importance of anaerobic respiration citing examples. Meets: Correctly describes the economic importance of anaerobic respiration. Approaches: Describes some of the economic importance. Below: Describes some with difficulty."},
                {"name": "Describe the mechanism of opening and closing of stomata in plants", "description": "describe the mechanism of opening and closing of stomata in plants"},
                {"name": "Investigate aerobic and anaerobic respiration in living organisms", "description": "investigate aerobic and anaerobic respiration in living organisms"},
                {"name": "Explain the economic importance of anaerobic respiration in nature", "description": "explain the economic importance of anaerobic respiration in nature"},
                {"name": "Appreciate the significance of gaseous exchange and respiration to plants and the environment", "description": "appreciate the significance of gaseous exchange and respiration to plants and the environment"}
            ]}
        ]},
        {"name": "3.0 Anatomy and Physiology of Animals", "substrands": [
            {"name": "3.1 Nutrition", "assessment_methods": ["Observation", "Drawing", "Discussions", "Written reports"], "slos": [
                {"name": "Relate the structure of mouthparts of insects to their functions", "description": "relate the structure of mouthparts of insects to their functions",
                 "assessment": "Exceeds: Correctly relates, providing illustrations of structure of mouthparts of insects to their functions. Meets: Correctly relates all structures of mouthparts of insects to their functions. Approaches: Relates some structures of mouthparts to their functions. Below: Relates some structures with difficulty."},
                {"name": "Illustrate mouthparts in different insects", "description": "illustrate mouthparts in different insects"},
                {"name": "Relate the structure of beaks of birds to their functions", "description": "relate the structure of beaks of birds to their functions"},
                {"name": "Appreciate diversity in feeding modes of insects and birds", "description": "appreciate diversity in feeding modes of insects and birds"}
            ]},
            {"name": "3.2 Transport", "assessment_methods": ["Research", "Drawing", "Dissection", "Chart preparation", "Discussions"], "slos": [
                {"name": "Explain the importance of transport in animals", "description": "explain the importance of transport in animals",
                 "assessment": "Exceeds: Comprehensively describes the pumping mechanism of the mammalian heart. Meets: Describes the pumping mechanism of the mammalian heart. Approaches: Partially describes the pumping mechanism. Below: Partially describes with prompts."},
                {"name": "Illustrate structure of the transport systems in insects, fish, amphibians, reptiles and mammals", "description": "illustrate structure of the transport systems in insects, fish, amphibians, reptiles and mammals"},
                {"name": "Describe the pumping mechanism of the mammalian heart", "description": "describe the pumping mechanism of the mammalian heart"},
                {"name": "Describe the human lymphatic and immune systems, and blood clotting mechanism", "description": "describe the human lymphatic and immune systems, and blood clotting mechanism"},
                {"name": "Explain the ABO and rhesus factor blood grouping systems in humans", "description": "explain the ABO and rhesus factor blood grouping systems in humans"},
                {"name": "Appreciate the diversity of transport systems in animals", "description": "appreciate the diversity of transport systems in animals"}
            ]},
            {"name": "3.3 Gaseous Exchange and Respiration", "assessment_methods": ["Observation", "Drawing", "Model construction", "Experiments", "Project work"], "slos": [
                {"name": "Explain the general characteristics of respiratory surfaces in animals", "description": "explain the general characteristics of respiratory surfaces in animals",
                 "assessment": "Exceeds: Comprehensively describes the process of aerobic and anaerobic respiration using illustrations. Meets: Describes the process of aerobic and anaerobic respiration. Approaches: Partially describes the process. Below: Partially describes with prompts."},
                {"name": "Describe the structure and adaptations of respiratory structures in animals", "description": "describe the structure and adaptations of respiratory structures in animals"},
                {"name": "Describe the mechanism of gaseous exchange in humans", "description": "describe the mechanism of gaseous exchange in humans"},
                {"name": "Describe the process of aerobic and anaerobic respiration", "description": "describe the process of aerobic and anaerobic respiration"},
                {"name": "Calculate the respiratory quotient for different foods", "description": "calculate the respiratory quotient for different foods"},
                {"name": "Appreciate the importance of gaseous exchange and respiration in animals", "description": "appreciate the importance of gaseous exchange and respiration in animals"}
            ]}
        ]}
    ]
    await seed_subject("Biology", biology)

    # ============================================================
    # CRE - 4 strands
    # ============================================================
    print("\nSeeding CRE...")
    cre = [
        {"name": "1.0 The Old Testament", "substrands": [
            {"name": "1.1 The Holy Bible", "assessment_methods": ["Checklists", "Journals", "Anecdotal Records", "Authentic Tasks"], "slos": [
                {"name": "Describe the Bible as the 'inspired' word of God", "description": "describe the Bible as the 'inspired' word of God",
                 "assessment": "Exceeds: Identifies five methods of studying the Bible and cites relevant examples. Meets: Identifies five methods. Approaches: Identifies four to three methods. Below: Identifies two to one methods."},
                {"name": "Identify human authors inspired to write the Holy Bible", "description": "identify human authors inspired to write the Holy Bible"},
                {"name": "Organise the Old Testament books according to their categories", "description": "organise the Old Testament books according to their categories"},
                {"name": "Distinguish the literary forms used in writing the Bible", "description": "distinguish the literary forms used in writing the Bible"},
                {"name": "Utilise the poetic form and present a song from the book of Psalms", "description": "utilise the poetic form and present a song from the book of Psalms"},
                {"name": "Acknowledge that the Bible is the inspired word of God", "description": "acknowledge that the Bible is the inspired word of God"}
            ]},
            {"name": "1.2 Methods of Studying the Holy Bible", "assessment_methods": ["Oral questions", "Rubrics", "Written tests", "Checklists", "Rating scales"], "slos": [
                {"name": "Summarize five methods of studying the Holy Bible", "description": "summarize five methods of studying the Holy Bible",
                 "assessment": "Exceeds: Explains six benefits of studying the Bible using illustrations. Meets: Explains six benefits. Approaches: Explains five to three benefits. Below: Explains two to one benefits."},
                {"name": "Examine the benefits of studying the Holy Bible", "description": "examine the benefits of studying the Holy Bible"},
                {"name": "Apply inductive method of studying the Bible to specific Bible texts", "description": "apply inductive method of studying the Bible to specific Bible texts"},
                {"name": "Utilise biography method to study the book of Jonah", "description": "utilise biography method to study the book of Jonah"},
                {"name": "Desire to read the word of God daily to grow spiritually", "description": "desire to read the word of God daily to grow spiritually"}
            ]},
            {"name": "1.3 Redemption after the Fall of Man", "assessment_methods": ["Questions and Answers", "Rating Scales", "Journals", "Checklists", "Authentic Tasks"], "slos": [
                {"name": "Explain the origin and consequences of sin", "description": "explain the origin and consequences of sin",
                 "assessment": "Exceeds: Explains the origin and consequences of sin and cites relevant scriptures. Meets: Explains the origin and consequences of sin as guided by the scriptures. Approaches: Explains but omits minor details. Below: Explains but omits major details."},
                {"name": "Elaborate God's plan of salvation after the fall of man", "description": "elaborate God's plan of salvation after the fall of man"},
                {"name": "Discuss ways Christians respond to God's redemptive work", "description": "discuss ways Christians respond to God's redemptive work"},
                {"name": "Desire to embrace God's redemptive work in day-to-day life", "description": "desire to embrace God's redemptive work in day-to-day life"}
            ]},
            {"name": "1.4 Stewardship Over Creation", "assessment_methods": ["Questionnaires", "Observation", "Checklists", "Journals", "Project"], "slos": [
                {"name": "Interpret the scriptures on stewardship", "description": "interpret the scriptures on stewardship",
                 "assessment": "Exceeds: Adapts the four principles of good stewardship in daily engagements and encourages peers to do so. Meets: Adapts the four principles. Approaches: Adapts three principles. Below: Adapts two principles."},
                {"name": "Deduce lessons learnt about stewardship for application in daily life", "description": "deduce lessons learnt about stewardship for application in daily life"},
                {"name": "Model qualities of good stewardship in day-to-day life", "description": "model qualities of good stewardship in day-to-day life"}
            ]},
            {"name": "1.5 The Exodus", "assessment_methods": ["Checklists", "Journals", "Anecdotal Records", "Authentic Tasks"], "slos": [
                {"name": "Dramatize the call of Moses as guided by the Holy scriptures", "description": "dramatize the call of Moses as guided by the Holy scriptures",
                 "assessment": "Exceeds: Creatively dramatizes the call of Moses and includes all the steps. Meets: Dramatizes the call of Moses. Approaches: Dramatizes but leaves out a few steps. Below: Dramatizes but leaves out many steps."},
                {"name": "Elaborate the discourse between God and Moses", "description": "elaborate the discourse between God and Moses"},
                {"name": "Restate the attributes of God from the ten plagues", "description": "restate the attributes of God from the ten plagues"},
                {"name": "Explain how the Passover foreshadows Jesus Christ's atonement", "description": "explain how the Passover foreshadows Jesus Christ's atonement"},
                {"name": "Summarize ways God cared for the Israelites during the Exodus", "description": "summarize ways God cared for the Israelites during the Exodus"},
                {"name": "Recognize God's power and deliverance during the Exodus", "description": "recognize God's power and deliverance during the Exodus"}
            ]},
            {"name": "1.6 The Sinai Covenant", "assessment_methods": ["Oral questions", "Rubrics", "Written tests", "Checklists", "Rating scales"], "slos": [
                {"name": "Describe the making of the Sinai Covenant", "description": "describe the making of the Sinai Covenant",
                 "assessment": "Exceeds: Exhaustively describes the making of the Sinai Covenant. Meets: Describes the making of the Sinai Covenant. Approaches: Describes but leaves out minor details. Below: Describes but leaves out major details."},
                {"name": "Apply the Ten Commandments in day-to-day life", "description": "apply the Ten Commandments in day-to-day life"},
                {"name": "Dramatize the breaking of the Sinai covenant", "description": "dramatize the breaking of the Sinai covenant"},
                {"name": "Illustrate the renewal of Sinai Covenant", "description": "illustrate the renewal of Sinai Covenant"},
                {"name": "Establish how the Israelites worshipped God in the wilderness", "description": "establish how the Israelites worshipped God in the wilderness"},
                {"name": "Take part in worshipping God at home, school and in church", "description": "take part in worshipping God at home, school and in church"}
            ]},
            {"name": "1.7 Loyalty to God", "assessment_methods": ["Observation", "Oral questions", "Rubrics", "Rating Scales", "Portfolio"], "slos": [
                {"name": "Identify forms of idol worship/religious extremism in the society today", "description": "identify forms of idol worship/religious extremism in the society today",
                 "assessment": "Exceeds: Identifies four forms of idol worship and gives relevant examples. Meets: Identifies four forms. Approaches: Identifies three to two forms. Below: Identifies only one form."},
                {"name": "Outline ways of discerning idol worship/ungodly groups as a Christian", "description": "outline ways of discerning idol worship/ungodly groups as a Christian"},
                {"name": "Analyse Elijah's fight against Baalism in Israel", "description": "analyse Elijah's fight against Baalism in Israel"},
                {"name": "Appraise circumstances surrounding Elijah's flight to Mount Horeb", "description": "appraise circumstances surrounding Elijah's flight to Mount Horeb"},
                {"name": "Analyse Elijah's fight against injustices in Israel", "description": "analyse Elijah's fight against injustices in Israel"},
                {"name": "Explore values and life skills needed to address social injustices in the society today", "description": "explore values and life skills needed to address social injustices in the society today"},
                {"name": "Desire to promote social justice at home, school and in the community", "description": "desire to promote social justice at home, school and in the community"}
            ]},
            {"name": "1.8 The Old Testament Prophets", "assessment_methods": ["Written Assignments", "Oral questions", "Rating Scales", "Peer Assessment", "Journals", "Portfolio"], "slos": [
                {"name": "Explain the meaning of the terms, prophet and prophecy", "description": "explain the meaning of the terms, prophet and prophecy",
                 "assessment": "Exceeds: Conclusively outlines categories of prophets in the Old Testament. Meets: Outlines categories. Approaches: Outlines three categories. Below: Outlines only one category."},
                {"name": "Outline categories of prophets in the Old Testament", "description": "outline categories of prophets in the Old Testament"},
                {"name": "Describe the importance of prophets in Israel", "description": "describe the importance of prophets in Israel"},
                {"name": "Analyse the relationship between the Old Testament and the New Testament prophecies", "description": "analyse the relationship between the Old Testament and the New Testament prophecies"},
                {"name": "Establish the relevance of prophecy to Christians today", "description": "establish the relevance of prophecy to Christians today"},
                {"name": "Utilize acquired knowledge to avoid being misled by false prophets", "description": "utilize acquired knowledge to avoid being misled by false prophets"}
            ]},
            {"name": "1.9.1 Background of Prophet Amos", "assessment_methods": ["Questionnaires", "Observation", "Checklists", "Journals", "Rating Scales"], "slos": [
                {"name": "Describe the background to the call of Prophet Amos", "description": "describe the background to the call of Prophet Amos",
                 "assessment": "Exceeds: Comprehensively elaborates the five visions of Prophet Amos and their relevance to Christians today. Meets: Elaborates the five visions. Approaches: Elaborates four to three visions. Below: Elaborates between two to one visions."},
                {"name": "Relate the call of prophet Amos as guided by the Bible Texts", "description": "relate the call of prophet Amos as guided by the Bible Texts"},
                {"name": "Elaborate the five visions of Prophet Amos and their relevance to Christians today", "description": "elaborate the five visions of Prophet Amos and their relevance to Christians today"},
                {"name": "Desire to exercise justice as guided by the teachings of prophet Amos", "description": "desire to exercise justice as guided by the teachings of prophet Amos"}
            ]},
            {"name": "1.9.2 Teachings of Prophet Amos", "assessment_methods": ["Oral questions", "Rubrics", "Written tests", "Checklists", "Rating scales"], "slos": [
                {"name": "Describe prophet Amos teachings and their relevance to Christians today", "description": "describe prophet Amos teachings and their relevance to Christians today",
                 "assessment": "Exceeds: Interprets the meaning of Remnant and Restoration and provides relevant examples. Meets: Interprets the meaning. Approaches: Attempts to interpret. Below: Interprets with consistent guidance."},
                {"name": "Explain Israel's election in light of the Bible texts provided", "description": "explain Israel's election in light of the Bible texts provided"},
                {"name": "Discuss the teachings of the day of the Lord and its relevance to Christians today", "description": "discuss the teachings of the day of the Lord and its relevance to Christians today"},
                {"name": "Interpret the meaning of Remnant and Restoration to the nation of Israel", "description": "interpret the meaning of Remnant and Restoration to the nation of Israel"},
                {"name": "Utilize acquired virtues in day-to-day life", "description": "utilize acquired virtues in day-to-day life"}
            ]}
        ]},
        {"name": "2.0 The New Testament", "substrands": [
            {"name": "2.1 The New Testament Books", "assessment_methods": ["Discussions", "Written tests", "Quizzes"], "slos": [
                {"name": "Organise the New Testament books according to their distinct categories", "description": "organise the New Testament books according to their distinct categories"},
                {"name": "Justify why the Bible is referred to as a library", "description": "justify why the Bible is referred to as a library"},
                {"name": "Establish ways the Bible is used in the society today", "description": "establish ways the Bible is used in the society today"},
                {"name": "Desire to read the Bible daily to grow spiritually", "description": "desire to read the Bible daily to grow spiritually"}
            ]},
            {"name": "2.2 Infancy and Early Life of Jesus Christ", "assessment_methods": ["Discussions", "Written tests", "Dramatization", "Quizzes"], "slos": [
                {"name": "Describe the fulfilment of the Old Testament prophecies", "description": "describe the fulfilment of the Old Testament prophecies",
                 "assessment": "Exceeds: Describes the fulfilment in detail. Meets: Describes the fulfilment. Approaches: Describes but omits minor details. Below: Describes but omits major details."},
                {"name": "Explain the role of John the Baptist as a link between the Old and the New Testament", "description": "explain the role of John the Baptist as a link between the Old and the New Testament"},
                {"name": "Elaborate the infancy and early life of Jesus Christ", "description": "elaborate the infancy and early life of Jesus Christ"},
                {"name": "Analyse the teachings of John the Baptist and their relevance to Christians today", "description": "analyse the teachings of John the Baptist and their relevance to Christians today"},
                {"name": "Describe the baptism of Jesus Christ and its relevance to Christians today", "description": "describe the baptism of Jesus Christ and its relevance to Christians today"},
                {"name": "Relate the temptations of Jesus Christ as guided by the scripture", "description": "relate the temptations of Jesus Christ as guided by the scripture"},
                {"name": "Utilize virtues exemplified by Jesus Christ to overcome temptations", "description": "utilize virtues exemplified by Jesus Christ to overcome temptations"}
            ]},
            {"name": "2.3 Galilean Ministry (selected teachings)", "assessment_methods": ["Discussions", "Written tests", "Dramatization", "Quizzes", "Presentations"], "slos": [
                {"name": "Describe Jesus Christ's rejection at Nazareth", "description": "describe Jesus Christ's rejection at Nazareth",
                 "assessment": "Exceeds: Exhaustively discusses the parables and their importance in the life of a Christian. Meets: Discusses the parables and their importance. Approaches: Discusses three parables. Below: Discusses only one parable."},
                {"name": "Elaborate Christ's opposition by the Pharisees and Scribes", "description": "elaborate Christ's opposition by the Pharisees and Scribes"},
                {"name": "Explain Jesus Christ's teachings on qualities of true discipleship", "description": "explain Jesus Christ's teachings on qualities of true discipleship"},
                {"name": "Deduce lessons learnt from the sermon on the plain as guided by Luke 6:17-49", "description": "deduce lessons learnt from the sermon on the plain as guided by Luke 6:17-49"},
                {"name": "Illustrate Jesus' works of compassion and their relevance to Christians today", "description": "illustrate Jesus' works of compassion and their relevance to Christians today"},
                {"name": "Relate the miracles of Jesus Christ and their significance", "description": "relate the miracles of Jesus Christ and their significance"},
                {"name": "Discuss the parables of Jesus Christ and their importance in the life of a Christian", "description": "discuss the parables of Jesus Christ and their importance in the life of a Christian"},
                {"name": "Desire to apply the teachings of Jesus Christ in day-to-day life", "description": "desire to apply the teachings of Jesus Christ in day-to-day life"}
            ]},
            {"name": "2.4 Paul's First Letter to the Corinthians", "assessment_methods": ["Discussions", "Written tests", "Quizzes"], "slos": [
                {"name": "Describe the causes of divisions in the Church of Corinth", "description": "describe the causes of divisions in the Church of Corinth",
                 "assessment": "Exceeds: Describes five causes and cites relevant examples. Meets: Describes five causes. Approaches: Describes four to three causes. Below: Describes between two and one cause."},
                {"name": "Discuss how Paul addressed divisions in the Church of Corinth", "description": "discuss how Paul addressed divisions in the Church of Corinth"},
                {"name": "Identify moral challenges facing the youth and suggest possible solutions", "description": "identify moral challenges facing the youth and suggest possible solutions"},
                {"name": "Analyse how Paul addressed the issue of immorality in the church of Corinth", "description": "analyse how Paul addressed the issue of immorality in the church of Corinth"},
                {"name": "Model good morals as guided by the teachings of Apostle Paul", "description": "model good morals as guided by the teachings of Apostle Paul"}
            ]}
        ]},
        {"name": "3.0 Church in Action", "substrands": [
            {"name": "3.1 The Holy Spirit", "assessment_methods": ["Oral questions", "Rubrics", "Written tests", "Rating scales"], "slos": [
                {"name": "Describe the outpouring of the Holy Spirit on the day of Pentecost", "description": "describe the outpouring of the Holy Spirit on the day of Pentecost",
                 "assessment": "Exceeds: Explains five Jesus' teachings on the role of the Holy Spirit citing relevant examples. Meets: Explains five teachings. Approaches: Explains four to three teachings. Below: Explains between two to one teachings."},
                {"name": "Relate Peter's message on the Day of Pentecost", "description": "relate Peter's message on the Day of Pentecost"},
                {"name": "Deduce lessons learnt from the day of Pentecost", "description": "deduce lessons learnt from the day of Pentecost"},
                {"name": "Explain Jesus' teachings on the role of the Holy Spirit", "description": "explain Jesus' teachings on the role of the Holy Spirit"},
                {"name": "Appreciate the role of the Holy Spirit in day-to-day life", "description": "appreciate the role of the Holy Spirit in day-to-day life"}
            ]},
            {"name": "3.2 The Gifts of the Holy Spirit", "assessment_methods": ["Written assignments", "Oral questions", "Observation", "Portfolio"], "slos": [
                {"name": "Classify the gifts of the Holy Spirit according to their categories", "description": "classify the gifts of the Holy Spirit according to their categories",
                 "assessment": "Exceeds: Comprehensively classifies the gifts according to their three categories. Meets: Classifies according to three categories. Approaches: Classifies in two categories. Below: Classifies in one category."},
                {"name": "Elaborate the criteria for discerning the gifts of the Holy Spirit", "description": "elaborate the criteria for discerning the gifts of the Holy Spirit"},
                {"name": "Appraise the manifestation of the gifts of the Holy Spirit in the Church today", "description": "appraise the manifestation of the gifts of the Holy Spirit in the Church today"},
                {"name": "Desire to receive the gifts of the Holy Spirit as guided by scriptures", "description": "desire to receive the gifts of the Holy Spirit as guided by scriptures"}
            ]},
            {"name": "3.3 The Holy Trinity", "assessment_methods": ["Checklists", "Journals", "Anecdotal Records", "Questions and Answers", "Rating Scales"], "slos": [
                {"name": "Explain the meaning of the Holy Trinity", "description": "explain the meaning of the Holy Trinity"},
                {"name": "Recite Philemon 1:3 to appreciate the Holy Trinity", "description": "recite Philemon 1:3 to appreciate the Holy Trinity"},
                {"name": "Describe three roles of the Holy Trinity", "description": "describe three roles of the Holy Trinity"},
                {"name": "Recognise the monotheistic doctrine in Christianity", "description": "recognise the monotheistic doctrine in Christianity"}
            ]},
            {"name": "3.4 Sacraments (Baptism, The Lord's Table or Eucharist)", "assessment_methods": ["Questionnaires", "Observation", "Checklists", "Journals", "Project"], "slos": [
                {"name": "Explain the meaning of baptism from the scriptures provided", "description": "explain the meaning of baptism from the scriptures provided"},
                {"name": "Elaborate the importance of baptism in the life of a Christian", "description": "elaborate the importance of baptism in the life of a Christian"},
                {"name": "Discuss how the Lord's table or Eucharist is celebrated in the church today", "description": "discuss how the Lord's table or Eucharist is celebrated in the church today"},
                {"name": "Explain the significance of the Lord's table or Eucharist in the life of a Christian", "description": "explain the significance of the Lord's table or Eucharist in the life of a Christian"},
                {"name": "Desire to participate in the sacraments to strengthen their faith in God", "description": "desire to participate in the sacraments to strengthen their faith in God"}
            ]}
        ]},
        {"name": "4.0 Christian Living Today", "substrands": [
            {"name": "4.1 Christian Ethics", "assessment_methods": ["Oral questions", "Rubrics", "Written tests", "Checklists", "Rating scales"], "slos": [
                {"name": "Explain the meaning of Christian ethics", "description": "explain the meaning of Christian ethics",
                 "assessment": "Exceeds: Comprehensively identifies five sources of Christian ethics. Meets: Identifies five sources. Approaches: Identifies four to three sources. Below: Identifies two to one source."},
                {"name": "Identify sources of Christian ethics", "description": "identify sources of Christian ethics"},
                {"name": "Analyse ethical issues facing the youth today", "description": "analyse ethical issues facing the youth today"},
                {"name": "Propose solutions to ethical issues facing the youth today", "description": "propose solutions to ethical issues facing the youth today"},
                {"name": "Utilize ethical values to make appropriate moral decisions in day-to-day life", "description": "utilize ethical values to make appropriate moral decisions in day-to-day life"}
            ]},
            {"name": "4.2 Human Rights (Non-Discrimination)", "assessment_methods": ["Checklists", "Journals", "Anecdotal Records", "Questions and Answers", "Rating Scales"], "slos": [
                {"name": "Outline types of gender based violence in Kenya today", "description": "outline types of gender based violence in Kenya today",
                 "assessment": "Exceeds: Outlines six types and cites relevant examples. Meets: Outlines six types. Approaches: Outlines five to three types. Below: Outlines between two to one type."},
                {"name": "Discuss causes of gender based violence and its effects on individuals and families", "description": "discuss causes of gender based violence and its effects on individuals and families"},
                {"name": "Apply the value of love in his/her interactions with others", "description": "apply the value of love in his/her interactions with others"},
                {"name": "Recognize that all human beings are created in the image and likeness of God", "description": "recognize that all human beings are created in the image and likeness of God"}
            ]},
            {"name": "4.3 Human Sexuality", "assessment_methods": ["Self-assessment", "Peer assessments", "Questions and Answers", "Journals", "Portfolio", "Checklists"], "slos": [
                {"name": "Explain the meaning of human sexuality", "description": "explain the meaning of human sexuality",
                 "assessment": "Exceeds: Proposes six ways of overcoming irresponsible sexual behaviour and cites relevant examples. Meets: Proposes six ways. Approaches: Proposes five to three ways. Below: Proposes two to one way."},
                {"name": "Elaborate Christian teachings on male-female relationships", "description": "elaborate Christian teachings on male-female relationships"},
                {"name": "Discuss the differences between dating and courtship", "description": "discuss the differences between dating and courtship"},
                {"name": "Outline types and causes of irresponsible sexual behaviour", "description": "outline types and causes of irresponsible sexual behaviour"},
                {"name": "Propose ways of overcoming irresponsible sexual behaviour", "description": "propose ways of overcoming irresponsible sexual behaviour"},
                {"name": "Desire to live responsibly as God fearing youths", "description": "desire to live responsibly as God fearing youths"}
            ]},
            {"name": "4.4 Marriage and Family", "assessment_methods": ["Oral questions", "Rubrics", "Written tests", "Rating scales"], "slos": [
                {"name": "Elaborate Christian teachings on marriage and family", "description": "elaborate Christian teachings on marriage and family",
                 "assessment": "Exceeds: Comprehensively discusses six challenges related to marriage and family. Meets: Discusses six challenges. Approaches: Discusses five to three challenges. Below: Discusses between two to one challenge."},
                {"name": "Explain celibacy as an alternative to marriage", "description": "explain celibacy as an alternative to marriage"},
                {"name": "Discuss challenges related to marriage and family", "description": "discuss challenges related to marriage and family"},
                {"name": "Recommend solutions to problems facing families today", "description": "recommend solutions to problems facing families today"},
                {"name": "Recognise marriage and families as sacred institutions ordained by God", "description": "recognise marriage and families as sacred institutions ordained by God"}
            ]},
            {"name": "4.5 Christian Response to Science and Technology", "assessment_methods": ["Questionnaires", "Observation", "Checklists", "Journals", "Project"], "slos": [
                {"name": "Explain the role of modern science and technology in advancing Christianity", "description": "explain the role of modern science and technology in advancing Christianity",
                 "assessment": "Exceeds: Comprehensively explains how modern science and technology has led to the spread of Christianity. Meets: Explains how modern science has led to the spread. Approaches: Attempts to explain. Below: With guidance explains."},
                {"name": "Discuss Christian views on issues related to modern science and technology", "description": "discuss Christian views on issues related to modern science and technology"},
                {"name": "Recognise God as the originator of witty inventions and creativity", "description": "recognise God as the originator of witty inventions and creativity"}
            ]}
        ]}
    ]
    await seed_subject("CRE", cre)

    # ============================================================
    # ELECTRICAL TECHNOLOGY - 4 strands
    # ============================================================
    print("\nSeeding Electrical Technology...")
    electrical = [
        {"name": "1.0 Fundamentals of Electrical Technology", "substrands": [
            {"name": "1.1 Introduction to Electrical Technology", "assessment_methods": ["Written tests", "Portfolio", "Observation", "Oral assessment"], "slos": [
                {"name": "Explain the importance of electrical technology in society", "description": "explain the importance of electrical technology in society"},
                {"name": "Identify career opportunities in the electrical technology field", "description": "identify career opportunities in the electrical technology field"},
                {"name": "Apply safety regulations while carrying out electrical tasks", "description": "apply safety regulations while carrying out electrical tasks"},
                {"name": "Explain the roles of stakeholders in application of electrical safety", "description": "explain the roles of stakeholders in application of electrical safety"},
                {"name": "Embrace electrical technology as a career in society", "description": "embrace electrical technology as a career in society"}
            ]},
            {"name": "1.2 D.C Electric Circuit", "assessment_methods": ["Practical tasks", "Observation", "Written tests"], "slos": [
                {"name": "Describe the properties of resistors in DC circuits", "description": "describe the properties of resistors in DC circuits",
                 "assessment": "Exceeds: Describes the properties with examples. Meets: Describes the properties. Approaches: Partly describes. Below: Describes with assistance."},
                {"name": "Analyse DC circuit using circuit laws", "description": "analyse DC circuit using circuit laws"},
                {"name": "Construct resistor networks in DC circuits", "description": "construct resistor networks in DC circuits"},
                {"name": "Troubleshoot DC circuits in electrical appliances", "description": "troubleshoot DC circuits in electrical appliances"},
                {"name": "Appreciate the practical application of DC circuits in day to day life", "description": "appreciate the practical application of DC circuits in day to day life"}
            ]},
            {"name": "1.3 Capacitors and Capacitance", "assessment_methods": ["Practical tasks", "Observation"], "slos": [
                {"name": "Describe the principle of operation of a capacitor in an electric circuit", "description": "describe the principle of operation of a capacitor in an electric circuit"},
                {"name": "Explain the characteristics of capacitive circuits", "description": "explain the characteristics of capacitive circuits"},
                {"name": "Select appropriate capacitors for use in a given application in electric circuits", "description": "select appropriate capacitors for use in a given application in electric circuits"},
                {"name": "Analyse series and parallel connection of capacitors in electric circuits", "description": "analyse series and parallel connection of capacitors in electric circuits"},
                {"name": "Appreciate the importance of capacitors in electrical appliances", "description": "appreciate the importance of capacitors in electrical appliances"}
            ]},
            {"name": "1.4 Cells and Batteries", "assessment_methods": ["Written tests", "Project work", "Observation"], "slos": [
                {"name": "Describe the principle of operation of a simple cell", "description": "describe the principle of operation of a simple cell"},
                {"name": "Connect series and parallel battery arrays in a circuit", "description": "connect series and parallel battery arrays in a circuit"},
                {"name": "Conduct battery charging procedure for a secondary battery", "description": "conduct battery charging procedure for a secondary battery"},
                {"name": "Perform maintenance procedures for cells and batteries for appliances", "description": "perform maintenance procedures for cells and batteries for appliances"},
                {"name": "Appreciate the importance of safe disposal of cells and batteries", "description": "appreciate the importance of safe disposal of cells and batteries"}
            ]}
        ]},
        {"name": "2.0 Electrical Machines", "substrands": [
            {"name": "2.1 Magnetism", "assessment_methods": ["Practical tasks", "Observation"], "slos": [
                {"name": "Explain the magnetic properties of materials", "description": "explain the magnetic properties of materials"},
                {"name": "Perform magnetization and demagnetization procedures of magnetic materials", "description": "perform magnetization and demagnetization procedures of magnetic materials"},
                {"name": "Draw magnetic field patterns around a magnet", "description": "draw magnetic field patterns around a magnet"},
                {"name": "Care for magnets used in equipment at a workplace", "description": "care for magnets used in equipment at a workplace"},
                {"name": "Appreciate application of magnets in day-to-day life", "description": "appreciate application of magnets in day-to-day life"}
            ]},
            {"name": "2.2 Electromagnetism", "assessment_methods": ["Practical tasks", "Observation"], "slos": [
                {"name": "Explain the principle of electromagnetism in electrical technology", "description": "explain the principle of electromagnetism in electrical technology"},
                {"name": "Establish the magnetic field pattern of a current carrying conductor", "description": "establish the magnetic field pattern of a current carrying conductor"},
                {"name": "Construct a solenoid for a given application", "description": "construct a solenoid for a given application"},
                {"name": "Construct an electromagnetic device for a given application", "description": "construct an electromagnetic device for a given application"},
                {"name": "Troubleshoot electromagnetic circuit in an appliance", "description": "troubleshoot electromagnetic circuit in an appliance"},
                {"name": "Appreciate the importance of electromagnetism in electrical devices and machines", "description": "appreciate the importance of electromagnetism in electrical devices and machines"}
            ]},
            {"name": "2.3 Measuring Instruments", "assessment_methods": ["Practical tasks", "Observation"], "slos": [
                {"name": "Explain the principle of operation of coil-based measuring instruments", "description": "explain the principle of operation of coil-based measuring instruments",
                 "assessment": "Exceeds: Precisely explains the principle of operation. Meets: Explains the principle. Approaches: Partially describes. Below: Hardly describes."},
                {"name": "Compute resistance values for shunts and multipliers of coil-based measuring instruments", "description": "compute resistance values for shunts and multipliers of coil-based measuring instruments"},
                {"name": "Calibrate coil based measuring instruments to ensure accuracy of measured quantities", "description": "calibrate coil based measuring instruments to ensure accuracy of measured quantities"},
                {"name": "Select a suitable scale for measuring a specified electrical quantity", "description": "select a suitable scale for measuring a specified electrical quantity"},
                {"name": "Recognise the importance of electrical measuring instruments", "description": "recognise the importance of electrical measuring instruments"}
            ]}
        ]},
        {"name": "3.0 Electrical Installation", "substrands": [
            {"name": "3.1 Generation, Transmission and Distribution of Electricity", "assessment_methods": ["Practical Tasks", "Observation", "Oral questions"], "slos": [
                {"name": "Describe methods of generation of electrical energy", "description": "describe methods of generation of electrical energy"},
                {"name": "Explain the functions of components in the electrical power transmission network", "description": "explain the functions of components in the electrical power transmission network"},
                {"name": "Draw a 3-phase 4 wire distribution circuit of a power line", "description": "draw a 3-phase 4 wire distribution circuit of a power line"},
                {"name": "Model an electric power Grid network", "description": "model an electric power Grid network"},
                {"name": "Appreciate the importance of a grid system in a country", "description": "appreciate the importance of a grid system in a country"}
            ]},
            {"name": "3.2 Equipment at Consumers Intake Point", "assessment_methods": ["Written tests", "Observation", "Oral questions"], "slos": [
                {"name": "Identify equipment at consumers electrical power intake point", "description": "identify equipment at consumers electrical power intake point",
                 "assessment": "Exceeds: Precisely and correctly identifies circuit protective devices. Meets: Correctly identifies. Approaches: Somewhat identifies. Below: Identifies with difficulty."},
                {"name": "Describe the functions of control equipment at the consumer's intake point", "description": "describe the functions of control equipment at the consumer's intake point"},
                {"name": "Install control equipment at the consumer's intake point in the correct sequence", "description": "install control equipment at the consumer's intake point in the correct sequence"},
                {"name": "Prepare consumer earthing point according to guiding regulations in a building", "description": "prepare consumer earthing point according to guiding regulations in a building"},
                {"name": "Appreciate the importance of the control equipment at the consumer intake point", "description": "appreciate the importance of the control equipment at the consumer intake point"}
            ]},
            {"name": "3.3 Final Circuits", "assessment_methods": ["Observation", "Written tests", "Practical tasks", "Project work"], "slos": [
                {"name": "Describe the final circuits in an electrical installation", "description": "describe the final circuits in an electrical installation"},
                {"name": "Interpret an electrical diagram according to established standards", "description": "interpret an electrical diagram according to established standards"},
                {"name": "Prepare a list of tools and materials required for a final circuit installation task", "description": "prepare a list of tools and materials required for a final circuit installation task"},
                {"name": "Install final circuits in an electrical installation work according to regulations", "description": "install final circuits in an electrical installation work according to regulations"},
                {"name": "Value the need for final circuits in an installation", "description": "value the need for final circuits in an installation"}
            ]}
        ]},
        {"name": "4.0 Electronics", "substrands": [
            {"name": "4.1 Semiconductor Theory", "assessment_methods": ["Written tests", "Practical tasks", "Observation"], "slos": [
                {"name": "Explain the characteristics of semiconductor materials", "description": "explain the characteristics of semiconductor materials",
                 "assessment": "Exceeds: Comprehensively and accurately explains. Meets: Accurately explains. Approaches: Partially explains. Below: Can explain with assistance."},
                {"name": "Describe the doping process in semiconductors", "description": "describe the doping process in semiconductors"},
                {"name": "Simulate covalent bonding in extrinsic semiconductors", "description": "simulate covalent bonding in extrinsic semiconductors"},
                {"name": "Illustrate formation of a PN junction of a semiconductor", "description": "illustrate formation of a PN junction of a semiconductor"},
                {"name": "Appreciate the importance of electronic materials in electronic engineering", "description": "appreciate the importance of electronic materials in electronic engineering"}
            ]},
            {"name": "4.2 Semiconductor Diodes", "assessment_methods": ["Written tests", "Practical tasks"], "slos": [
                {"name": "Describe the operation of a semiconductor diode", "description": "describe the operation of a semiconductor diode"},
                {"name": "Explain the current-voltage characteristics of semiconductor diodes", "description": "explain the current-voltage characteristics of semiconductor diodes"},
                {"name": "Construct diode circuits for use in a workplace", "description": "construct diode circuits for use in a workplace"},
                {"name": "Troubleshoot diode circuits in electrical appliances", "description": "troubleshoot diode circuits in electrical appliances"},
                {"name": "Appreciate the importance of semiconductor diodes in day to day life", "description": "appreciate the importance of semiconductor diodes in day to day life"}
            ]},
            {"name": "4.3 Transistors", "assessment_methods": ["Written tests", "Practical tasks", "Project work"], "slos": [
                {"name": "Describe the operation of semiconductor transistors", "description": "describe the operation of semiconductor transistors"},
                {"name": "Verify the voltage versus current characteristic of transistors", "description": "verify the voltage versus current characteristic of transistors"},
                {"name": "Select an appropriate transistor for a given application", "description": "select an appropriate transistor for a given application"},
                {"name": "Construct transistor circuits in a workplace", "description": "construct transistor circuits in a workplace"},
                {"name": "Appreciate the importance of transistors in electronics", "description": "appreciate the importance of transistors in electronics"}
            ]}
        ]}
    ]
    await seed_subject("Electrical Technology", electrical)

    # ============================================================
    # ENGLISH - 9 units with multiple strands each
    # ============================================================
    print("\nSeeding English...")
    english = [
        {"name": "1.0 Listening, Speaking, Reading, Grammar and Writing (Unit 1)", "substrands": [
            {"name": "1.1.1 Listening: Extensive Listening", "assessment_methods": ["Oral narration", "Discussions", "Questions and answers"], "slos": [
                {"name": "Describe characters, places and memorable events from a recording", "description": "describe characters, places and memorable events from a recording",
                 "assessment": "Exceeds: Identifies key details from a variety of oral texts for information. Meets: Identifies key details from an oral text. Approaches: Identifies most key details. Below: Identifies only a few with assistance."},
                {"name": "Listen to a recording and pick key details for general information", "description": "listen to a recording and pick key details for general information"},
                {"name": "Recount a story or dialogue in an oral context for enjoyment", "description": "recount a story or dialogue in an oral context for enjoyment"},
                {"name": "Acknowledge the role of identifying key information for lifelong learning", "description": "acknowledge the role of identifying key information for lifelong learning"}
            ]},
            {"name": "1.1.2 Speaking: Etiquette", "assessment_methods": ["Oral presentations", "Debates", "Discussions"], "slos": [
                {"name": "Pick out the target sounds and aspects of etiquette in oral or written texts", "description": "pick out the target sounds and aspects of etiquette in oral or written texts"},
                {"name": "Use appropriate etiquette in different contexts", "description": "use appropriate etiquette in different contexts"},
                {"name": "Articulate the sounds for effective communication", "description": "articulate the sounds for effective communication"},
                {"name": "Justify the need for accurate pronunciation in communication", "description": "justify the need for accurate pronunciation in communication"}
            ]},
            {"name": "1.2.1 Reading Fluency", "assessment_methods": ["Reading aloud", "Oral questions", "Written assignments"], "slos": [
                {"name": "Preview a text and make predictions about characters, people and places", "description": "preview a text and make predictions about characters, people and places"},
                {"name": "Skim varied texts while glossing over unknown words to obtain the gist", "description": "skim varied texts while glossing over unknown words to obtain the gist"},
                {"name": "Scan a text to obtain specific details", "description": "scan a text to obtain specific details"},
                {"name": "Predict how words collocate for effective communication", "description": "predict how words collocate for effective communication"},
                {"name": "Acknowledge the importance of reading fluency in lifelong learning", "description": "acknowledge the importance of reading fluency in lifelong learning"}
            ]},
            {"name": "1.3.1 Word Classes: Nouns, Pronouns and Determiners", "assessment_methods": ["Filling in gaps", "Substitution tables", "Cloze test", "Oral questions"], "slos": [
                {"name": "Classify nouns in sentences", "description": "classify nouns in sentences"},
                {"name": "Recognise the various types of pronouns in varied contexts", "description": "recognise the various types of pronouns in varied contexts"},
                {"name": "Differentiate the use of words as pronouns and determiners in sentences", "description": "differentiate the use of words as pronouns and determiners in sentences"},
                {"name": "Use nouns and pronouns in sentences", "description": "use nouns and pronouns in sentences"},
                {"name": "Acknowledge the importance of the correct usage of nouns, pronouns and determiners", "description": "acknowledge the importance of the correct usage of nouns, pronouns and determiners"}
            ]},
            {"name": "1.5.1 Sentence Fluency", "assessment_methods": ["Written exercises", "Peer assessment", "Rewriting exercises"], "slos": [
                {"name": "Contrast well-written sentences with comma splices, run on sentences and run on lines", "description": "contrast well-written sentences with comma splices, run on sentences and run on lines",
                 "assessment": "Exceeds: Rewrites comma splices, run on sentences and run on lines as complete sentences with consistency. Meets: Rewrites them as complete sentences. Approaches: Rewrites in most cases. Below: Rewrites but with assistance."},
                {"name": "Rewrite comma splices, run on sentences and run on lines as complete sentences", "description": "rewrite comma splices, run on sentences and run on lines as complete sentences"},
                {"name": "Value the importance of well-written sentences in communication", "description": "value the importance of well-written sentences in communication"}
            ]}
        ]},
        {"name": "2.0 Listening, Speaking, Reading, Grammar and Writing (Unit 2)", "substrands": [
            {"name": "2.1.1 Critical Listening", "assessment_methods": ["Oral narration", "Discussions", "Questions and answers"], "slos": [
                {"name": "Describe various forms of distractions to effective listening", "description": "describe various forms of distractions to effective listening"},
                {"name": "Determine the speaker, context and intention in varied oral texts", "description": "determine the speaker, context and intention in varied oral texts"},
                {"name": "Select key points from an audio text for information", "description": "select key points from an audio text for information"},
                {"name": "Appreciate the importance of critical listening in communication", "description": "appreciate the importance of critical listening in communication"}
            ]},
            {"name": "2.1.2 Conversational Skills", "assessment_methods": ["Oral presentations", "Debates", "Discussions"], "slos": [
                {"name": "Classify discourse markers used in a variety of texts", "description": "classify discourse markers used in a variety of texts",
                 "assessment": "Exceeds: Uses discourse markers ingeniously to organise ideas. Meets: Uses discourse markers to organise ideas. Approaches: Uses in most instances. Below: Uses but with cues."},
                {"name": "Articulate the sounds for oral fluency", "description": "articulate the sounds for oral fluency"},
                {"name": "Use discourse markers to organise ideas during conversations", "description": "use discourse markers to organise ideas during conversations"},
                {"name": "Apply onomatopoeic words and idiophones in oral communication", "description": "apply onomatopoeic words and idiophones in oral communication"},
                {"name": "Advocate the need to organise ideas appropriately in oral communication", "description": "advocate the need to organise ideas appropriately in oral communication"}
            ]},
            {"name": "2.2.1 Extensive Reading", "assessment_methods": ["Reading aloud", "Oral questions", "Written assignments"], "slos": [
                {"name": "Select a text in preparation for reading", "description": "select a text in preparation for reading"},
                {"name": "Read varied texts for enjoyment and general understanding", "description": "read varied texts for enjoyment and general understanding"},
                {"name": "Recognise the role of extensive reading in building vocabulary", "description": "recognise the role of extensive reading in building vocabulary"}
            ]},
            {"name": "2.3.1 Word Classes: Verbs and Adverbs", "assessment_methods": ["Filling in gaps", "Substitution tables", "Cloze test"], "slos": [
                {"name": "Identify main verbs and primary auxiliary verbs from texts", "description": "identify main verbs and primary auxiliary verbs from texts"},
                {"name": "Inflect verbs appropriately to show tense and aspect", "description": "inflect verbs appropriately to show tense and aspect"},
                {"name": "Use main verbs and primary auxiliary verbs in sentences", "description": "use main verbs and primary auxiliary verbs in sentences"},
                {"name": "Use adverbs of time, place and manner in sentence construction", "description": "use adverbs of time, place and manner in sentence construction"},
                {"name": "Acknowledge the role of verbs, tense, aspect and adverbs in communicating precisely", "description": "acknowledge the role of verbs, tense, aspect and adverbs in communicating precisely"}
            ]},
            {"name": "2.5.1 Mechanics of Writing", "assessment_methods": ["Written exercises", "Dictation", "Peer assessment"], "slos": [
                {"name": "Identify frequently misspelt and easily confused words in written texts", "description": "identify frequently misspelt and easily confused words in written texts"},
                {"name": "Use acronyms, commonly misspelt and easily confused words in sentences", "description": "use acronyms, commonly misspelt and easily confused words in sentences"},
                {"name": "Apply spelling rules to write words with affixes for effective communication", "description": "apply spelling rules to write words with affixes for effective communication"},
                {"name": "Appreciate the role of abbreviations and acronyms in written texts", "description": "appreciate the role of abbreviations and acronyms in written texts"}
            ]}
        ]},
        {"name": "3.0 Listening, Speaking, Reading, Grammar and Writing (Unit 3)", "substrands": [
            {"name": "3.1.1 Intensive Listening", "assessment_methods": ["Oral narration", "Discussions"], "slos": [
                {"name": "Select specific details from a listening text", "description": "select specific details from a listening text"},
                {"name": "Use words and phrases picked from an oral text in a variety of contexts", "description": "use words and phrases picked from an oral text in a variety of contexts"},
                {"name": "Advocate the need to discriminate among sounds for effective communication", "description": "advocate the need to discriminate among sounds for effective communication"}
            ]},
            {"name": "3.1.2 Nonverbal Cues", "assessment_methods": ["Oral presentations", "Discussions"], "slos": [
                {"name": "Identify target sounds in oral texts", "description": "identify target sounds in oral texts"},
                {"name": "Articulate target sounds for oral fluency", "description": "articulate target sounds for oral fluency"},
                {"name": "Use nonverbal cues appropriately in oral communication", "description": "use nonverbal cues appropriately in oral communication",
                 "assessment": "Exceeds: Uses non-verbal cues appropriately and creatively. Meets: Uses non-verbal cues appropriately. Approaches: Uses appropriately most of the time. Below: Uses but with prompting."},
                {"name": "Acknowledge the importance of articulating sounds accurately", "description": "acknowledge the importance of articulating sounds accurately"}
            ]},
            {"name": "3.2.1 Extensive Reading: Reference Materials", "assessment_methods": ["Reading aloud", "Oral questions", "Written assignments"], "slos": [
                {"name": "Explain the uses of the thesaurus and dictionaries for enhancement of reading skills", "description": "explain the uses of the thesaurus and dictionaries"},
                {"name": "Pick out information from atlases, manuals, newspapers and encyclopedias for general knowledge", "description": "pick out information from atlases, manuals, newspapers and encyclopedias"},
                {"name": "Appreciate the importance of reference materials as a source of information", "description": "appreciate the importance of reference materials as a source of information"}
            ]},
            {"name": "3.3.1 Word Classes: Adjectives, Prepositions and Conjunctions", "assessment_methods": ["Filling in gaps", "Substitution tables", "Cloze test"], "slos": [
                {"name": "Identify adjectives, simple prepositions and coordinating conjunctions from written texts", "description": "identify adjectives, simple prepositions and coordinating conjunctions"},
                {"name": "Use simple prepositions and coordinating conjunctions in sentences", "description": "use simple prepositions and coordinating conjunctions in sentences"},
                {"name": "Order adjectives correctly in sentences", "description": "order adjectives correctly in sentences"},
                {"name": "Recognise the importance of using adjectives, simple prepositions and conjunctions", "description": "recognise the importance of using adjectives, simple prepositions and conjunctions"}
            ]},
            {"name": "3.5.1 Elements of Effective Writing", "assessment_methods": ["Written exercises", "Peer assessment", "Creative writing"], "slos": [
                {"name": "Explain the use of connectors of addition, similarity and contrast in a text", "description": "explain the use of connectors of addition, similarity and contrast",
                 "assessment": "Exceeds: Orders ideas in a paragraph for coherence in a variety of contexts. Meets: Orders ideas for coherence. Approaches: Partially orders ideas. Below: Orders ideas when prompted."},
                {"name": "Order ideas in a paragraph for coherence", "description": "order ideas in a paragraph for coherence"},
                {"name": "Write a coherent paragraph on a given topic", "description": "write a coherent paragraph on a given topic"},
                {"name": "Acknowledge the value of logically ordering ideas in writing", "description": "acknowledge the value of logically ordering ideas in writing"}
            ]}
        ]},
        {"name": "4.0 Listening, Speaking, Reading, Grammar and Writing (Unit 4-5)", "substrands": [
            {"name": "4.1.1 Selective Listening", "assessment_methods": ["Oral narration", "Discussions"], "slos": [
                {"name": "Describe ways of selecting specific information from a listening text", "description": "describe ways of selecting specific information from a listening text"},
                {"name": "Listen to an oral text and filter instructions and directions", "description": "listen to an oral text and filter instructions and directions"},
                {"name": "Take notes from a variety of listening texts", "description": "take notes from a variety of listening texts"},
                {"name": "Argue for the need to listen attentively to extract specific details", "description": "argue for the need to listen attentively to extract specific details"}
            ]},
            {"name": "4.1.2 Conversational Skills: Topic Change and Feedback", "assessment_methods": ["Oral presentations", "Debates"], "slos": [
                {"name": "Describe the techniques of changing the topic in a conversation", "description": "describe the techniques of changing the topic in a conversation"},
                {"name": "Give and receive feedback in the communication process", "description": "give and receive feedback in the communication process"},
                {"name": "Distinguish between formal and informal register in communication", "description": "distinguish between formal and informal register in communication"},
                {"name": "Acknowledge the importance of conversation skills in effective communication", "description": "acknowledge the importance of conversation skills in effective communication"}
            ]},
            {"name": "4.2.1 Study Skills: SQ4R", "assessment_methods": ["Reading aloud", "Oral questions", "Written assignments"], "slos": [
                {"name": "Outline steps in summary and note making for improving comprehension", "description": "outline steps in summary and note making"},
                {"name": "Use the SQ4R technique and summary and note making skills for study purposes", "description": "use the SQ4R technique and summary and note making skills"},
                {"name": "Analyse visual information in a reading context", "description": "analyse visual information in a reading context"},
                {"name": "Acknowledge the importance of using effective study skills", "description": "acknowledge the importance of using effective study skills"}
            ]},
            {"name": "4.3.1 Phrases: Noun Phrase and Verb Phrase", "assessment_methods": ["Filling in gaps", "Cloze test", "Oral questions"], "slos": [
                {"name": "Identify the constituents of the noun phrase and verb phrase", "description": "identify the constituents of the noun phrase and verb phrase"},
                {"name": "Use the noun phrase and verb phrase for fluency in oral and written texts", "description": "use the noun phrase and verb phrase for fluency"},
                {"name": "Advocate the correct usage of noun phrases and verb phrases", "description": "advocate the correct usage of noun phrases and verb phrases"}
            ]},
            {"name": "4.5.1 Mechanics of Writing: Punctuation", "assessment_methods": ["Written exercises", "Dictation", "Peer assessment"], "slos": [
                {"name": "Explain the punctuation principles of capitalisation, quotation marks, dashes, hyphens and slashes", "description": "explain the punctuation principles of capitalisation, quotation marks, dashes, hyphens and slashes"},
                {"name": "Use the target punctuation marks to write sentences", "description": "use the target punctuation marks to write sentences"},
                {"name": "Apply the rules of capitalisation in a variety of sentences", "description": "apply the rules of capitalisation in a variety of sentences"},
                {"name": "Advocate the correct use of punctuation marks in sentences", "description": "advocate the correct use of punctuation marks in sentences"}
            ]},
            {"name": "5.1.1 Interactive Listening", "assessment_methods": ["Oral narration", "Discussions"], "slos": [
                {"name": "Establish instances of turn-taking and negotiating meaning in a dialogue", "description": "establish instances of turn-taking and negotiating meaning"},
                {"name": "Clarify the speaker's meaning in a conversation", "description": "clarify the speaker's meaning in a conversation"},
                {"name": "Show empathy towards the speaker for effective social relations", "description": "show empathy towards the speaker for effective social relations"},
                {"name": "Advocate the importance of listening to understand for peaceful co-existence", "description": "advocate the importance of listening to understand"}
            ]},
            {"name": "5.1.2 Speaking: Etiquette and Pronunciation", "assessment_methods": ["Oral presentations", "Debates"], "slos": [
                {"name": "Explain how to take turns, interrupt and disagree politely", "description": "explain how to take turns, interrupt and disagree politely"},
                {"name": "Interrupt and disagree politely for peaceful co-existence", "description": "interrupt and disagree politely for peaceful co-existence"},
                {"name": "Practise turn taking in a variety of contexts", "description": "practise turn taking in a variety of contexts"},
                {"name": "Promote the need to observe etiquette in oral communication", "description": "promote the need to observe etiquette in oral communication"}
            ]},
            {"name": "5.2.1 Intensive Reading", "assessment_methods": ["Reading aloud", "Rubrics", "Written assignments"], "slos": [
                {"name": "Evaluate their understanding of a text for comprehension", "description": "evaluate their understanding of a text for comprehension",
                 "assessment": "Exceeds: Answers direct and inferential questions from texts with precision. Meets: Answers direct and inferential questions. Approaches: Answers most. Below: Answers few."},
                {"name": "Make predictions about events, people and places in a text", "description": "make predictions about events, people and places in a text"},
                {"name": "Answer direct and inferential questions from a text", "description": "answer direct and inferential questions from a text"},
                {"name": "Infer the meaning of words and phrases in a written text", "description": "infer the meaning of words and phrases in a written text"},
                {"name": "Promote the role of reading comprehension in learning", "description": "promote the role of reading comprehension in learning"}
            ]},
            {"name": "5.3.1 Phrases: Adverb, Adjective and Prepositional", "assessment_methods": ["Filling in gaps", "Substitution tables", "Cloze test"], "slos": [
                {"name": "Analyse the constituents of adverb, adjective and prepositional phrases", "description": "analyse the constituents of adverb, adjective and prepositional phrases"},
                {"name": "Describe the functions of the adverb, adjective and prepositional phrases", "description": "describe the functions of the adverb, adjective and prepositional phrases"},
                {"name": "Use adverb, adjective and prepositional phrases in varied contexts", "description": "use adverb, adjective and prepositional phrases in varied contexts"},
                {"name": "Appreciate the use of the adverb, adjective and prepositional phrases", "description": "appreciate the use of the adverb, adjective and prepositional phrases"}
            ]},
            {"name": "5.5.1 The Writing Process", "assessment_methods": ["Written exercises", "Functional writing"], "slos": [
                {"name": "Explain the steps of the writing process in institutional writing", "description": "explain the steps of the writing process in institutional writing"},
                {"name": "Write an appreciation letter adhering to the steps of the writing process", "description": "write an appreciation letter adhering to the steps of the writing process"},
                {"name": "Appreciate the importance of following the writing process for lifelong learning", "description": "appreciate the importance of following the writing process for lifelong learning"}
            ]}
        ]},
        {"name": "5.0 Listening, Speaking, Reading, Grammar and Writing (Unit 6-7)", "substrands": [
            {"name": "6.1.1 Responsive Listening", "assessment_methods": ["Oral narration", "Discussions"], "slos": [
                {"name": "Outline techniques for listening to respond for problem solving", "description": "outline techniques for listening to respond for problem solving"},
                {"name": "Listen to a text to find solutions to problems", "description": "listen to a text to find solutions to problems"},
                {"name": "Relate oral texts to personal experiences for critical thinking", "description": "relate oral texts to personal experiences for critical thinking",
                 "assessment": "Exceeds: Relates oral texts to personal experiences in a variety of contexts. Meets: Relates oral texts to personal experiences. Approaches: Partially relates. Below: Relates but with prompting."},
                {"name": "Contribute to solving social problems in a variety of contexts", "description": "contribute to solving social problems in a variety of contexts"}
            ]},
            {"name": "6.1.2 Pronunciation and Syllabic Stress", "assessment_methods": ["Oral presentations", "Debates"], "slos": [
                {"name": "Distinguish word classes on the basis of stress", "description": "distinguish word classes on the basis of stress",
                 "assessment": "Exceeds: Applies syllabic stress meticulously in speech. Meets: Applies syllabic stress correctly. Approaches: Applies in most instances. Below: Applies but with assistance."},
                {"name": "Place stress in disyllabic words correctly in oral communication", "description": "place stress in disyllabic words correctly"},
                {"name": "Pronounce words with target sounds accurately", "description": "pronounce words with target sounds accurately"},
                {"name": "Champion the need to stress words correctly for clear communication", "description": "champion the need to stress words correctly"}
            ]},
            {"name": "6.2.1 Reading Fluency: Expressive Reading", "assessment_methods": ["Reading aloud", "Rubrics"], "slos": [
                {"name": "Discuss the features of expressive reading from a selected text", "description": "discuss the features of expressive reading"},
                {"name": "Read a text with expression to bring out pitch, pace, volume and intonation", "description": "read a text with expression to bring out pitch, pace, volume and intonation"},
                {"name": "Promote the value of expressive reading for lifelong learning", "description": "promote the value of expressive reading for lifelong learning"}
            ]},
            {"name": "6.3.1 Clauses: Relative and Adverbial", "assessment_methods": ["Filling in gaps", "Substitution tables", "Cloze test"], "slos": [
                {"name": "Pick out relative and adverbial clauses in sentences", "description": "pick out relative and adverbial clauses in sentences"},
                {"name": "Distinguish between defining and non-defining relative clauses", "description": "distinguish between defining and non-defining relative clauses"},
                {"name": "Use relative clauses and adverbial clauses in varied contexts", "description": "use relative clauses and adverbial clauses in varied contexts"},
                {"name": "Advocate the correct use of relative clauses and adverbial clauses", "description": "advocate the correct use of relative clauses and adverbial clauses"}
            ]},
            {"name": "6.5.1 Creative Writing: Descriptive Narrative", "assessment_methods": ["Creative writing", "Peer assessment", "Written exercises"], "slos": [
                {"name": "Describe a person in a variety of ways for literary effect", "description": "describe a person in a variety of ways for literary effect",
                 "assessment": "Exceeds: Captivatingly writes a descriptive narrative essay on a variety of topics. Meets: Writes a descriptive narrative essay. Approaches: Writes a flat and colourless essay. Below: Writes with a lot of assistance."},
                {"name": "Write a descriptive narrative essay on given topics", "description": "write a descriptive narrative essay on given topics"},
                {"name": "Advocate the use of sensory details in descriptive writing", "description": "advocate the use of sensory details in descriptive writing"}
            ]},
            {"name": "7.1.1 Critical Listening: Facts and Opinions", "assessment_methods": ["Oral narration", "Discussions"], "slos": [
                {"name": "Recognise opinions from an audio recording", "description": "recognise opinions from an audio recording"},
                {"name": "Explain facts in a given oral text", "description": "explain facts in a given oral text"},
                {"name": "Distinguish facts from opinions in an oral context", "description": "distinguish facts from opinions in an oral context"},
                {"name": "Advocate the relevance of distinguishing facts and opinions", "description": "advocate the relevance of distinguishing facts and opinions"}
            ]},
            {"name": "7.1.2 Pronunciation and Emphatic Stress", "assessment_methods": ["Oral presentations", "Debates"], "slos": [
                {"name": "Recognise the different realisations of target sounds in writing", "description": "recognise the different realisations of target sounds in writing"},
                {"name": "Articulate target sounds and blends in varied texts", "description": "articulate target sounds and blends in varied texts"},
                {"name": "Use emphatic stress in sentences for enhanced meaning", "description": "use emphatic stress in sentences for enhanced meaning"},
                {"name": "Promote the need for correct pronunciation and stress placement", "description": "promote the need for correct pronunciation and stress placement"}
            ]},
            {"name": "7.2.1 Intensive Reading: Comprehension", "assessment_methods": ["Reading aloud", "Rubrics", "Written assignments"], "slos": [
                {"name": "Create mental images about people, places or happenings in a text", "description": "create mental images about people, places or happenings",
                 "assessment": "Exceeds: Summarises information from a variety of texts with precision. Meets: Summarises information from a text. Approaches: Summarises in most instances. Below: Summarises in few instances."},
                {"name": "Infer the meaning of words and phrases for comprehension", "description": "infer the meaning of words and phrases for comprehension"},
                {"name": "Relate information in a text to real life situations", "description": "relate information in a text to real life situations"},
                {"name": "Summarise information from a text for comprehension", "description": "summarise information from a text for comprehension"},
                {"name": "Appreciate the importance of reading comprehension in lifelong learning", "description": "appreciate the importance of reading comprehension in lifelong learning"}
            ]},
            {"name": "7.3.1 Clauses: Noun Clauses", "assessment_methods": ["Filling in gaps", "Substitution tables"], "slos": [
                {"name": "Recognise the noun clause that begin with that and what from a given context", "description": "recognise the noun clause that begin with that and what"},
                {"name": "Use noun clauses in varied contexts", "description": "use noun clauses in varied contexts"},
                {"name": "Acknowledge the importance of the noun clause in communication", "description": "acknowledge the importance of the noun clause in communication"}
            ]},
            {"name": "7.5.1 Functional Writing: Letters", "assessment_methods": ["Written exercises", "Functional writing"], "slos": [
                {"name": "Identify the appropriate format and content of complaint, request and inquiry letters", "description": "identify the appropriate format of complaint, request and inquiry letters",
                 "assessment": "Exceeds: Writes both items using the correct format, language and organisation meticulously. Meets: Writes using the correct format. Approaches: Writes but is not consistent. Below: Hardly writes using the correct format."},
                {"name": "Write letters of complaint, request and inquiry in varied situations", "description": "write letters of complaint, request and inquiry"},
                {"name": "Acknowledge the role of letter writing in effective communication", "description": "acknowledge the role of letter writing in effective communication"}
            ]}
        ]},
        {"name": "6.0 Listening, Speaking, Reading, Grammar and Writing (Unit 8-9)", "substrands": [
            {"name": "8.1.1 Intensive Listening/Viewing", "assessment_methods": ["Oral narration", "Discussions"], "slos": [
                {"name": "Recognise non-verbal cues and visuals from an audiovisual presentation", "description": "recognise non-verbal cues and visuals from an audiovisual presentation"},
                {"name": "Interpret non-verbal cues in an oral text for meaning", "description": "interpret non-verbal cues in an oral text for meaning"},
                {"name": "Infer meaning from visuals in audiovisual texts", "description": "infer meaning from visuals in audiovisual texts"},
                {"name": "Acknowledge the role of non-verbal cues in decoding meaning", "description": "acknowledge the role of non-verbal cues in decoding meaning"}
            ]},
            {"name": "8.1.2 Speaking Fluency", "assessment_methods": ["Oral presentations", "Debates"], "slos": [
                {"name": "Distinguish among synonyms, antonyms and homophones in communication", "description": "distinguish among synonyms, antonyms and homophones",
                 "assessment": "Exceeds: Pronounces the target words correctly for fluency. Meets: Pronounces the target words correctly. Approaches: Pronounces most correctly. Below: Pronounces a few correctly."},
                {"name": "Describe a speaker's accuracy, expressiveness and speed in an oral presentation", "description": "describe a speaker's accuracy, expressiveness and speed"},
                {"name": "Perform an oral narrative with accuracy, expression and at the right speed", "description": "perform an oral narrative with accuracy, expression and at the right speed"},
                {"name": "Influence others to use synonyms, antonyms and homophones accurately", "description": "influence others to use synonyms, antonyms and homophones accurately"}
            ]},
            {"name": "8.2.1 Extensive Reading: Library Skills", "assessment_methods": ["Reading aloud", "Oral questions", "Written assignments"], "slos": [
                {"name": "Discuss the steps involved in library research for information", "description": "discuss the steps involved in library research",
                 "assessment": "Exceeds: Locates print and non-print resources in libraries and databases with consistency. Meets: Locates resources. Approaches: Locates most of the time. Below: Locates but with a lot of guidance."},
                {"name": "Locate print and non-print resources in libraries and databases", "description": "locate print and non-print resources in libraries and databases"},
                {"name": "Appreciate the need for libraries in schools as foundations for research", "description": "appreciate the need for libraries in schools as foundations for research"}
            ]},
            {"name": "8.3.1 Sentence Structure: Simple and Compound", "assessment_methods": ["Filling in gaps", "Substitution tables", "Cloze test"], "slos": [
                {"name": "Analyse the SV, SVO, SVC, SVOO, SVOA patterns in simple sentences", "description": "analyse the SV, SVO, SVC, SVOO, SVOA patterns in simple sentences"},
                {"name": "Use simple sentences in oral and written texts", "description": "use simple sentences in oral and written texts"},
                {"name": "Use compound sentences in oral and written texts", "description": "use compound sentences in oral and written texts"},
                {"name": "Recognise the importance of using a variety of sentences", "description": "recognise the importance of using a variety of sentences"}
            ]},
            {"name": "8.5.1 Functional Writing: Reports, Memos and Emails", "assessment_methods": ["Written exercises", "Functional writing"], "slos": [
                {"name": "Identify the elements of simple reports, memos and emails", "description": "identify the elements of simple reports, memos and emails"},
                {"name": "Write simple reports, memos and emails for writing fluency", "description": "write simple reports, memos and emails for writing fluency"},
                {"name": "Advocate the need to produce well-written reports, memos and emails", "description": "advocate the need to produce well-written reports, memos and emails"}
            ]},
            {"name": "9.1.1 Selective Listening", "assessment_methods": ["Oral narration", "Discussions"], "slos": [
                {"name": "Identify strategies for listening to specific details from an oral text", "description": "identify strategies for listening to specific details"},
                {"name": "Extract specific information from an oral narrative", "description": "extract specific information from an oral narrative"},
                {"name": "Embrace the importance of listening for particular information", "description": "embrace the importance of listening for particular information"}
            ]},
            {"name": "9.1.2 Speaking Fluency: Intonation", "assessment_methods": ["Oral presentations", "Debates"], "slos": [
                {"name": "Differentiate consonant sounds in oral communication", "description": "differentiate consonant sounds in oral communication"},
                {"name": "Apply appropriate intonation in different types of sentences", "description": "apply appropriate intonation in different types of sentences"},
                {"name": "Analyse aspects of fluency in an informative skit", "description": "analyse aspects of fluency in an informative skit"},
                {"name": "Acknowledge the importance of speaking fluently in various contexts", "description": "acknowledge the importance of speaking fluently in various contexts"}
            ]},
            {"name": "9.2.1 Critical/Close Reading", "assessment_methods": ["Reading aloud", "Rubrics", "Written assignments"], "slos": [
                {"name": "Explain how to identify the audience, purpose and attitude in a text", "description": "explain how to identify the audience, purpose and attitude in a text"},
                {"name": "Determine the audience, purpose and attitude in a reading text", "description": "determine the audience, purpose and attitude in a reading text"},
                {"name": "Use transparent phrasal verbs and binomial expressions in sentences", "description": "use transparent phrasal verbs and binomial expressions"},
                {"name": "Recognise the importance of critical and close reading", "description": "recognise the importance of critical and close reading"}
            ]},
            {"name": "9.3.1 Sentences: Subject-Verb Agreement and Voice", "assessment_methods": ["Filling in gaps", "Cloze test"], "slos": [
                {"name": "Explain the basic rules of subject-verb agreement in sentences", "description": "explain the basic rules of subject-verb agreement"},
                {"name": "Examine the agreement of subject-verb in sentences", "description": "examine the agreement of subject-verb in sentences"},
                {"name": "Distinguish between active and passive sentences in a text", "description": "distinguish between active and passive sentences"},
                {"name": "Construct active and passive sentences for variety in communication", "description": "construct active and passive sentences for variety"},
                {"name": "Advocate for the use of a variety of sentences", "description": "advocate for the use of a variety of sentences"}
            ]},
            {"name": "9.5.1 Functional Writing: Meeting Documents", "assessment_methods": ["Written exercises", "Functional writing"], "slos": [
                {"name": "Describe the features of notice of a meeting, agenda and minutes", "description": "describe the features of notice of a meeting, agenda and minutes"},
                {"name": "Write a notice of a meeting and the agenda for communication", "description": "write a notice of a meeting and the agenda"},
                {"name": "Prepare the attendant minutes for information", "description": "prepare the attendant minutes for information"},
                {"name": "Recognise the value of documents related to meetings", "description": "recognise the value of documents related to meetings"}
            ]}
        ]}
    ]
    await seed_subject("English", english)

    # ============================================================
    # FASIHI YA KISWAHILI - 3 strands
    # ============================================================
    print("\nSeeding Fasihi ya Kiswahili...")
    fasihi = [
        {"name": "1.0 Fasihi Simulizi", "substrands": [
            {"name": "1.1 Utangulizi wa Fasihi Simulizi", "assessment_methods": ["Majadiliano", "Utafiti", "Uwasilishaji"], "slos": [
                {"name": "Kueleza maana ya fasihi ili kuibainisha", "description": "kueleza maana ya fasihi ili kuibainisha",
                 "assessment": "Kuzidisha: Anachambua hadithi za fasihi simulizi kwa kina na kwa utondoti, akizingatia vipengele vyake. Kufikia: Anachambua hadithi za fasihi simulizi kwa kuzingatia vipengele vyake. Kukaribia: Anachambua kwa kuzingatia baadhi ya vipengele vyake. Mbali: Anachambua kwa kuzingatia baadhi ya vipengele vyake kwa kuelekezwa."},
                {"name": "Kueleza maana ya fasihi simulizi ili kuibainisha", "description": "kueleza maana ya fasihi simulizi ili kuibainisha"},
                {"name": "Kufafanua sifa za fasihi simulizi", "description": "kufafanua sifa za fasihi simulizi"},
                {"name": "Kujadili umuhimu wa fasihi simulizi katika jamii", "description": "kujadili umuhimu wa fasihi simulizi katika jamii"},
                {"name": "Kuchangamkia fasihi simulizi katika jamii", "description": "kuchangamkia fasihi simulizi katika jamii"}
            ]},
            {"name": "2.1 Hadithi: Hekaya na Hurafa", "assessment_methods": ["Majadiliano", "Uchambuzi", "Ubunifu"], "slos": [
                {"name": "Kueleza maana ya hadithi ili kuibainisha", "description": "kueleza maana ya hadithi ili kuibainisha"},
                {"name": "Kueleza maana ya hekaya na hurafa ili kuzibainisha", "description": "kueleza maana ya hekaya na hurafa ili kuzibainisha"},
                {"name": "Kufafanua sifa za hekaya na hurafa ili kuzipambanua", "description": "kufafanua sifa za hekaya na hurafa ili kuzipambanua"},
                {"name": "Kujadili umuhimu wa hekaya na hurafa katika jamii", "description": "kujadili umuhimu wa hekaya na hurafa katika jamii"},
                {"name": "Kuwasilisha hekaya na hurafa akizingatia vipengele vya uwasilishaji", "description": "kuwasilisha hekaya na hurafa akizingatia vipengele vya uwasilishaji"},
                {"name": "Kuchangamkia masimulizi ya hekaya na hurafa katika jamii", "description": "kuchangamkia masimulizi ya hekaya na hurafa katika jamii"}
            ]},
            {"name": "3.1 Semi", "assessment_methods": ["Utafiti", "Majadiliano", "Uchambuzi"], "slos": [
                {"name": "Kueleza maana ya semi katika fasihi simulizi", "description": "kueleza maana ya semi katika fasihi simulizi",
                 "assessment": "Kuzidisha: Anachanganua semi za fasihi simulizi kwa kina na kwa utondoti, akizingatia vipengele vyake. Kufikia: Anachanganua semi kwa kuzingatia vipengele vyake. Kukaribia: Anachanganua kwa kuzingatia baadhi ya vipengele. Mbali: Anachanganua kwa kusaidiwa."},
                {"name": "Kufafanua sifa za semi katika fasihi simulizi", "description": "kufafanua sifa za semi katika fasihi simulizi"},
                {"name": "Kujadili umuhimu wa semi katika jamii", "description": "kujadili umuhimu wa semi katika jamii"},
                {"name": "Kuainisha vipera vya semi ili kuvibainisha", "description": "kuainisha vipera vya semi ili kuvibainisha"},
                {"name": "Kufurahia matumizi ya vipera mbalimbali vya semi", "description": "kufurahia matumizi ya vipera mbalimbali vya semi katika fasihi simulizi"}
            ]},
            {"name": "4.1 Ushairi Simulizi", "assessment_methods": ["Majadiliano", "Uwasilishaji", "Ubunifu"], "slos": [
                {"name": "Kueleza maana ya ushairi simulizi ili kuubainisha", "description": "kueleza maana ya ushairi simulizi ili kuubainisha",
                 "assessment": "Kuzidisha: Anachanganua mashairi simulizi kwa kina na kwa utondoti, akizingatia vipengele vyake. Kufikia: Anachanganua mashairi simulizi kwa kuzingatia vipengele vyake. Kukaribia: Anachanganua kwa kuzingatia baadhi ya vipengele. Mbali: Anachanganua kwa kusaidiwa."},
                {"name": "Kufafanua sifa za ushairi simulizi ili kuzipambanua", "description": "kufafanua sifa za ushairi simulizi ili kuzipambanua"},
                {"name": "Kuchambua sifa za ushairi simulizi katika simulizi", "description": "kuchambua sifa za ushairi simulizi katika simulizi"},
                {"name": "Kujadili dhima za ushairi simulizi katika jamii", "description": "kujadili dhima za ushairi simulizi katika jamii"},
                {"name": "Kuchangamkia ushairi simulizi katika jamii", "description": "kuchangamkia ushairi simulizi katika jamii"}
            ]},
            {"name": "6.1 Maigizo", "assessment_methods": ["Majadiliano", "Uigizaji", "Utafiti"], "slos": [
                {"name": "Kueleza dhana ya maigizo ili kuibainisha", "description": "kueleza dhana ya maigizo ili kuibainisha",
                 "assessment": "Kuzidisha: Anachambua maigizo ya fasihi simulizi kwa uketo, akizingatia vipengele vyake. Kufikia: Anachambua maigizo kwa kuzingatia vipengele vyake. Kukaribia: Anachambua kwa kuzingatia baadhi ya vipengele. Mbali: Anachambua kwa kuongozwa."},
                {"name": "Kufafanua sifa za maigizo ili kuzibainisha", "description": "kufafanua sifa za maigizo ili kuzibainisha"},
                {"name": "Kujadili umuhimu wa maigizo katika jamii", "description": "kujadili umuhimu wa maigizo katika jamii"},
                {"name": "Kuigiza vipera vya maigizo ya fasihi simulizi", "description": "kuigiza vipera vya maigizo ya fasihi simulizi"},
                {"name": "Kuchangamkia umuhimu wa maigizo katika jamii yake", "description": "kuchangamkia umuhimu wa maigizo katika jamii yake"}
            ]},
            {"name": "10.1 Maghani ya Kawaida", "assessment_methods": ["Majadiliano", "Utafiti", "Uwasilishaji", "Ubunifu"], "slos": [
                {"name": "Kueleza maana ya maghani ya kawaida kama kipera cha ushairi simulizi", "description": "kueleza maana ya maghani ya kawaida kama kipera cha ushairi simulizi"},
                {"name": "Kueleza maana ya majigambo, pembezi na tondozi kama aina za maghani ya kawaida", "description": "kueleza maana ya majigambo, pembezi na tondozi"},
                {"name": "Kueleza sifa za majigambo, pembezi na tondozi", "description": "kueleza sifa za majigambo, pembezi na tondozi"},
                {"name": "Kujadili umuhimu wa majigambo, pembezi na tondozi katika jamii", "description": "kujadili umuhimu wa majigambo, pembezi na tondozi katika jamii"},
                {"name": "Kueleza vipengele vya majigambo, pembezi na tondozi", "description": "kueleza vipengele vya majigambo, pembezi na tondozi"},
                {"name": "Kuchanganua vipengele vya majigambo, pembezi na tondozi katika matini", "description": "kuchanganua vipengele vya majigambo, pembezi na tondozi katika matini"},
                {"name": "Kufurahia matumizi ya majigambo, pembezi na tondozi katika miktadha mbalimbali", "description": "kufurahia matumizi ya majigambo, pembezi na tondozi katika miktadha mbalimbali"}
            ]}
        ]},
        {"name": "2.0 Ushairi", "substrands": [
            {"name": "1.2 Uainishaji wa Ushairi", "assessment_methods": ["Majadiliano", "Utafiti", "Uchambuzi"], "slos": [
                {"name": "Kueleza maana ya ushairi ili kuupambanua", "description": "kueleza maana ya ushairi ili kuupambanua",
                 "assessment": "Kuzidisha: Anaainisha mashairi kwa kuzingatia vigezo mbalimbali vya uainishaji kwa utondoti. Kufikia: Anaainisha mashairi kwa kuzingatia vigezo mbalimbali. Kukaribia: Anaainisha kwa kuzingatia baadhi ya vigezo. Mbali: Anaainisha kwa kuelekezwa."},
                {"name": "Kujadili sifa za ushairi kama utanzu wa fasihi", "description": "kujadili sifa za ushairi kama utanzu wa fasihi"},
                {"name": "Kuchambua sifa za ushairi katika mashairi mbalimbali", "description": "kuchambua sifa za ushairi katika mashairi mbalimbali"},
                {"name": "Kufafanua dhima ya ushairi katika jamii", "description": "kufafanua dhima ya ushairi katika jamii"},
                {"name": "Kuchangamkia aina mbalimbali za mashairi katika jamii", "description": "kuchangamkia aina mbalimbali za mashairi katika jamii"}
            ]},
            {"name": "2.2 Uchambuzi wa Mashairi: Makundi ya Mashairi", "assessment_methods": ["Majadiliano", "Utafiti", "Uchambuzi"], "slos": [
                {"name": "Kueleza maana za ushairi arudhi na ushairi huru ili kuzipambanua", "description": "kueleza maana za ushairi arudhi na ushairi huru",
                 "assessment": "Kuzidisha: Anachambua mashairi kwa kina, akizingatia vipengele mbalimbali vya ushairi. Kufikia: Anachambua mashairi kwa kuzingatia vipengele. Kukaribia: Anachambua kwa kuzingatia baadhi ya vipengele. Mbali: Anachambua kwa kusaidiwa."},
                {"name": "Kujadili sifa za ushairi arudhi na ushairi huru", "description": "kujadili sifa za ushairi arudhi na ushairi huru"},
                {"name": "Kutambua mashairi arudhi na mashairi huru katika matini", "description": "kutambua mashairi arudhi na mashairi huru katika matini"},
                {"name": "Kuchangamkia makundi makuu ya ushairi katika fasihi", "description": "kuchangamkia makundi makuu ya ushairi katika fasihi"}
            ]},
            {"name": "3.2 Uchambuzi wa Maudhui na Dhamira", "assessment_methods": ["Uchambuzi", "Utafiti", "Uwasilishaji"], "slos": [
                {"name": "Kueleza maana za maudhui na dhamira ili kuzibainisha", "description": "kueleza maana za maudhui na dhamira ili kuzibainisha"},
                {"name": "Kuchambua maudhui na dhamira katika mashairi", "description": "kuchambua maudhui na dhamira katika mashairi"},
                {"name": "Kufurahia kuchambua maudhui na dhamira katika mashairi", "description": "kufurahia kuchambua maudhui na dhamira katika mashairi"}
            ]},
            {"name": "6.2 Uchambuzi wa Muundo", "assessment_methods": ["Majadiliano", "Uchambuzi", "Utafiti"], "slos": [
                {"name": "Kueleza maana ya muundo ili kuupambanua", "description": "kueleza maana ya muundo ili kuupambanua"},
                {"name": "Kujadili vipengele vya muundo katika mashairi", "description": "kujadili vipengele vya muundo katika mashairi"},
                {"name": "Kufafanua umuhimu wa vipengele vya muundo katika shairi", "description": "kufafanua umuhimu wa vipengele vya muundo"},
                {"name": "Kuchambua mashairi kwa kuzingatia vipengele vya muundo", "description": "kuchambua mashairi kwa kuzingatia vipengele vya muundo"},
                {"name": "Kufurahia kuchambua mashairi kwa kuzingatia vipengele vyake", "description": "kufurahia kuchambua mashairi kwa kuzingatia vipengele vyake"}
            ]},
            {"name": "7.2 Mtindo - Sitiari, Tashihisi, Tashbihi", "assessment_methods": ["Uchambuzi", "Utafiti", "Majadiliano"], "slos": [
                {"name": "Kueleza maana ya tashbihi, sitiari na tashihisi kama vipengele vya kimtindo", "description": "kueleza maana ya tashbihi, sitiari na tashihisi"},
                {"name": "Kutambua tashbihi, sitiari na tashihisi katika ushairi", "description": "kutambua tashbihi, sitiari na tashihisi katika ushairi"},
                {"name": "Kujadili umuhimu wa tashbihi, sitiari na tashihisi katika ushairi", "description": "kujadili umuhimu wa tashbihi, sitiari na tashihisi katika ushairi"},
                {"name": "Kutathmini nafasi ya tashbihi, sitiari na tashihisi katika mashairi", "description": "kutathmini nafasi ya tashbihi, sitiari na tashihisi katika mashairi"},
                {"name": "Kufurahia matumizi ya tashbihi, sitiari na tashihisi katika mashairi", "description": "kufurahia matumizi ya tashbihi, sitiari na tashihisi"}
            ]},
            {"name": "8.2 Mtindo - Misemo, Nahau, Chuku", "assessment_methods": ["Uchambuzi", "Utafiti", "Uwasilishaji"], "slos": [
                {"name": "Kueleza maana ya misemo, nahau na chuku kama vipengele vya kimtindo", "description": "kueleza maana ya misemo, nahau na chuku"},
                {"name": "Kutambua misemo, nahau na chuku katika matini za kishairi", "description": "kutambua misemo, nahau na chuku katika matini za kishairi"},
                {"name": "Kueleza umuhimu wa misemo, nahau na chuku katika ushairi", "description": "kueleza umuhimu wa misemo, nahau na chuku"},
                {"name": "Kutathmini nafasi ya misemo, nahau na chuku katika ushairi", "description": "kutathmini nafasi ya misemo, nahau na chuku"},
                {"name": "Kufurahia matumizi ya misemo, nahau na chuku katika ushairi", "description": "kufurahia matumizi ya misemo, nahau na chuku"}
            ]},
            {"name": "9.1 Ushairi Simulizi - Nyimbo", "assessment_methods": ["Majadiliano", "Uchambuzi", "Utafiti", "Ubunifu"], "slos": [
                {"name": "Kueleza maana ya nyimbo kama kipera cha ushairi simulizi", "description": "kueleza maana ya nyimbo kama kipera cha ushairi simulizi"},
                {"name": "Kujadili aina mbalimbali za nyimbo katika fasihi simulizi", "description": "kujadili aina mbalimbali za nyimbo katika fasihi simulizi"},
                {"name": "Kufafanua sifa za nyimbo katika ushairi simulizi", "description": "kufafanua sifa za nyimbo katika ushairi simulizi"},
                {"name": "Kujadili dhima za nyimbo katika jamii", "description": "kujadili dhima za nyimbo katika jamii"},
                {"name": "Kuchanganua nyimbo kwa kuzingatia sifa zake", "description": "kuchanganua nyimbo kwa kuzingatia sifa zake"},
                {"name": "Kufurahia nyimbo za aina mbalimbali kutoka jamii tofauti tofauti", "description": "kufurahia nyimbo za aina mbalimbali kutoka jamii tofauti tofauti"}
            ]},
            {"name": "9.2 Uhuru wa Kishairi - Inkisari, Mazida, Tabdila", "assessment_methods": ["Majadiliano", "Utafiti", "Uchambuzi"], "slos": [
                {"name": "Kueleza maana ya uhuru wa kishairi ili kuipambanua", "description": "kueleza maana ya uhuru wa kishairi ili kuipambanua"},
                {"name": "Kueleza maana ya inkisari, mazida, tabdila na kuboronga sarufi", "description": "kueleza maana ya inkisari, mazida, tabdila na kuboronga sarufi"},
                {"name": "Kutambua matumizi ya inkisari, mazida, tabdila na kuboronga sarufi katika mashairi", "description": "kutambua matumizi ya inkisari, mazida, tabdila na kuboronga sarufi"},
                {"name": "Kujadili umuhimu wa inkisari, mazida, tabdila na kuboronga sarufi katika mashairi", "description": "kujadili umuhimu wa inkisari, mazida, tabdila na kuboronga sarufi"},
                {"name": "Kufurahia matumizi ya inkisari, mazida, tabdila na kuboronga sarufi katika mashairi", "description": "kufurahia matumizi ya inkisari, mazida, tabdila na kuboronga sarufi"}
            ]},
            {"name": "10.2 Utunzi wa Mashairi na Bunilizi", "assessment_methods": ["Majadiliano", "Utafiti", "Utunzi", "Uwasilishaji"], "slos": [
                {"name": "Kutambua vipengele vya utunzi wa mashairi na bunilizi ili kuvibainisha", "description": "kutambua vipengele vya utunzi wa mashairi na bunilizi",
                 "assessment": "Kuzidisha: Anatunga bunilizi ya kiwango cha juu cha ubunifu kwa kuzingatia vipengele na hatua zifaazo. Kufikia: Anatunga bunilizi kwa kuzingatia vipengele na hatua. Kukaribia: Anatunga kwa kuzingatia baadhi ya vipengele. Mbali: Anaelekezwa kutunga."},
                {"name": "Kupambanua hatua za utunzi wa mashairi na bunilizi ili kuzitambulisha", "description": "kupambanua hatua za utunzi wa mashairi na bunilizi"},
                {"name": "Kuandika shairi au bunilizi fupi kwa kuzingatia vipengele na hatua za utunzi", "description": "kuandika shairi au bunilizi fupi kwa kuzingatia vipengele na hatua za utunzi"},
                {"name": "Kuonea fahari utunzi wa bunilizi katika maisha ya kila siku", "description": "kuonea fahari utunzi wa bunilizi katika maisha ya kila siku"}
            ]}
        ]},
        {"name": "3.0 Bunilizi", "substrands": [
            {"name": "1.3 Utangulizi wa Bunilizi", "assessment_methods": ["Utafiti", "Uwasilishaji", "Uchambuzi"], "slos": [
                {"name": "Kueleza maana ya bunilizi ili kuibainisha", "description": "kueleza maana ya bunilizi ili kuibainisha",
                 "assessment": "Kuzidisha: Anachambua kwa utondoti vipengele vyote vya bunilizi. Kufikia: Anachambua vipengele vyote vya bunilizi. Kukaribia: Anachambua baadhi ya vipengele. Mbali: Anachambua baadhi ya vipengele kwa kuelekezwa."},
                {"name": "Kujadili aina za bunilizi ili kuzibainisha", "description": "kujadili aina za bunilizi ili kuzibainisha"},
                {"name": "Kujadili vipengele vya bunilizi", "description": "kujadili vipengele vya bunilizi"},
                {"name": "Kuchangamkia usomaji wa bunilizi katika maisha ya kila siku", "description": "kuchangamkia usomaji wa bunilizi katika maisha ya kila siku"}
            ]},
            {"name": "2.3 Tamthilia - Maudhui - Dhamira", "assessment_methods": ["Majadiliano", "Uchambuzi", "Uwasilishaji"], "slos": [
                {"name": "Kueleza maana ya maudhui na dhamira katika fasihi", "description": "kueleza maana ya maudhui na dhamira katika fasihi"},
                {"name": "Kujadili maudhui na dhamira katika tamthilia teule", "description": "kujadili maudhui na dhamira katika tamthilia teule"},
                {"name": "Kuchambua maudhui na dhamira katika tamthilia teule", "description": "kuchambua maudhui na dhamira katika tamthilia teule"},
                {"name": "Kuchangamkia maudhui na dhamira katika tamthilia mbalimbali", "description": "kuchangamkia maudhui na dhamira katika tamthilia mbalimbali"}
            ]},
            {"name": "3.3 Tamthilia - Wahusika - Mandhari", "assessment_methods": ["Majadiliano", "Utafiti", "Uchambuzi"], "slos": [
                {"name": "Kueleza dhana ya wahusika na mandhari katika tamthilia", "description": "kueleza dhana ya wahusika na mandhari katika tamthilia"},
                {"name": "Kujadili usawiri wa wahusika katika tamthilia teule", "description": "kujadili usawiri wa wahusika katika tamthilia teule"},
                {"name": "Kueleza umuhimu wa wahusika katika tamthilia teule", "description": "kueleza umuhimu wa wahusika katika tamthilia teule"},
                {"name": "Kueleza umuhimu wa mandhari katika tamthilia", "description": "kueleza umuhimu wa mandhari katika tamthilia"},
                {"name": "Kujadili aina za mandhari katika tamthilia", "description": "kujadili aina za mandhari katika tamthilia"},
                {"name": "Kuchangamkia wahusika na mandhari katika tamthilia", "description": "kuchangamkia wahusika na mandhari katika tamthilia"}
            ]},
            {"name": "4.3 Tamthilia - Muundo - Mtindo", "assessment_methods": ["Majadiliano", "Utafiti", "Uchambuzi"], "slos": [
                {"name": "Kueleza maana ya muundo na mtindo katika tamthilia", "description": "kueleza maana ya muundo na mtindo katika tamthilia"},
                {"name": "Kutambua vipengele vya muundo na mtindo katika tamthilia", "description": "kutambua vipengele vya muundo na mtindo katika tamthilia"},
                {"name": "Kujadili vipengele vya muundo na mtindo katika tamthilia teule", "description": "kujadili vipengele vya muundo na mtindo katika tamthilia teule"},
                {"name": "Kutathmini nafasi ya vipengele vya muundo na mtindo", "description": "kutathmini nafasi ya vipengele vya muundo na mtindo katika tamthilia teule"},
                {"name": "Kuchambua tamthilia teule kwa kuzingatia muundo na mtindo wake", "description": "kuchambua tamthilia teule kwa kuzingatia muundo na mtindo wake"},
                {"name": "Kuonea fahari muundo na mtindo katika tamthilia", "description": "kuonea fahari muundo na mtindo katika tamthilia"}
            ]},
            {"name": "5.3 Riwaya - Muundo - Mtindo", "assessment_methods": ["Majadiliano", "Utafiti", "Uchambuzi"], "slos": [
                {"name": "Kueleza maana ya muundo na mtindo katika riwaya", "description": "kueleza maana ya muundo na mtindo katika riwaya"},
                {"name": "Kujadili vipengele vya muundo na mtindo katika fasihi", "description": "kujadili vipengele vya muundo na mtindo katika fasihi"},
                {"name": "Kuchanganua muundo na mtindo katika riwaya", "description": "kuchanganua muundo na mtindo katika riwaya"},
                {"name": "Kuchangamkia muundo na mtindo katika riwaya", "description": "kuchangamkia muundo na mtindo katika riwaya"}
            ]},
            {"name": "6.3 Riwaya - Maudhui - Dhamira", "assessment_methods": ["Majadiliano", "Uchambuzi", "Utafiti"], "slos": [
                {"name": "Kueleza maana ya maudhui na dhamira katika riwaya teule", "description": "kueleza maana ya maudhui na dhamira katika riwaya teule"},
                {"name": "Kutambua maudhui na dhamira katika riwaya teule", "description": "kutambua maudhui na dhamira katika riwaya teule"},
                {"name": "Kueleza namna maudhui yanavyowasilishwa katika riwaya", "description": "kueleza namna maudhui yanavyowasilishwa katika riwaya"},
                {"name": "Kuchanganua maudhui na dhamira katika riwaya teule", "description": "kuchanganua maudhui na dhamira katika riwaya teule"},
                {"name": "Kuchangamkia maudhui na dhamira katika riwaya", "description": "kuchangamkia maudhui na dhamira katika riwaya"}
            ]},
            {"name": "7.3 Riwaya - Wahusika - Mandhari", "assessment_methods": ["Majadiliano", "Utafiti", "Uchambuzi"], "slos": [
                {"name": "Kueleza dhana ya wahusika na mandhari katika riwaya", "description": "kueleza dhana ya wahusika na mandhari katika riwaya"},
                {"name": "Kujadili usawiri wa wahusika katika riwaya teule", "description": "kujadili usawiri wa wahusika katika riwaya teule"},
                {"name": "Kueleza umuhimu wa wahusika katika riwaya", "description": "kueleza umuhimu wa wahusika katika riwaya"},
                {"name": "Kueleza umuhimu wa mandhari katika riwaya", "description": "kueleza umuhimu wa mandhari katika riwaya"},
                {"name": "Kujadili aina za mandhari katika riwaya", "description": "kujadili aina za mandhari katika riwaya"},
                {"name": "Kuchangamkia wahusika na mandhari katika riwaya", "description": "kuchangamkia wahusika na mandhari katika riwaya"}
            ]},
            {"name": "9.3 Riwaya - Muundo - Mtindo", "assessment_methods": ["Majadiliano", "Utafiti", "Uchambuzi"], "slos": [
                {"name": "Kueleza maana ya muundo na mtindo katika riwaya", "description": "kueleza maana ya muundo na mtindo katika riwaya"},
                {"name": "Kujadili vipengele vya muundo na mtindo katika fasihi", "description": "kujadili vipengele vya muundo na mtindo katika fasihi"},
                {"name": "Kuchanganua muundo na mtindo katika riwaya", "description": "kuchanganua muundo na mtindo katika riwaya"},
                {"name": "Kuchangamkia muundo na mtindo katika riwaya", "description": "kuchangamkia muundo na mtindo katika riwaya"}
            ]}
        ]}
    ]
    await seed_subject("Fasihi ya Kiswahili", fasihi)

    # --- SUMMARY ---
    total_subjects = await db.subjects.count_documents({"gradeIds": grade_id})
    total_strands = await db.strands.count_documents({})
    total_substrands = await db.substrands.count_documents({})
    total_slos = await db.slos.count_documents({})
    total_mappings = await db.slo_mappings.count_documents({})
    non_empty_mappings = await db.slo_mappings.count_documents({"competencyIds": {"$ne": []}})

    print(f"\n=== SEEDING COMPLETE ===")
    print(f"Grade 10 Subjects: {total_subjects}")
    print(f"Total Strands: {total_strands}")
    print(f"Total Sub-strands: {total_substrands}")
    print(f"Total SLOs: {total_slos}")
    print(f"Total SLO Mappings: {total_mappings}")
    print(f"Mappings with competencies: {non_empty_mappings}/{total_mappings}")

    client.close()

asyncio.run(seed())
