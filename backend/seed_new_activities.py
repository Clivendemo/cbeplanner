#!/usr/bin/env python3
"""
Seed learning activities for the 5 new subjects.
These activities will be used in lesson plan generation.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Learning Activities for the 5 new subjects
ACTIVITIES_DATA = {
    "Business Studies": {
        "Business and Money Management": {
            "Money": {
                "introduction": [
                    "Teacher displays samples of Kenyan currency and asks learners to identify security features.",
                    "Brainstorm on why people keep money and its importance in daily transactions.",
                    "Show video clips on ethical and unethical practices in the use of money."
                ],
                "development": [
                    "Discuss and present on security features and themes of money using actual currency samples.",
                    "Share experiences on why people demand money in the economy.",
                    "Role play functions of money: medium of exchange, store of value, unit of account, standard of deferred payment.",
                    "Read and analyse case studies on the demand for and supply of money in Kenya.",
                    "Brainstorm on factors determining money supply: government policy, bank lending, foreign exchange."
                ],
                "conclusion": [
                    "Summarize the key functions of money in financial transactions.",
                    "Present findings on ethical practices in use of money.",
                    "Reflect on the importance of money management in daily life."
                ],
                "extended": [
                    "Research on the evolution of money in Kenya from barter to digital currency.",
                    "Create a poster on ethical use of money for display in school.",
                    "Interview a bank official about money management practices."
                ]
            },
            "Business Goals": {
                "introduction": [
                    "Teacher asks: What do you want to achieve in life? How is this similar to business goals?",
                    "Brainstorm on the meaning and importance of goal setting in personal and business contexts.",
                    "Display examples of business goals from successful Kenyan entrepreneurs."
                ],
                "development": [
                    "Discuss and present on the meaning and importance of goal setting in business.",
                    "Brainstorm factors to consider when setting business goals: resources, time, competition.",
                    "Use digital resources to search for steps in setting SMART business goals.",
                    "Practice setting SMART (Specific, Measurable, Achievable, Relevant, Time-bound) goals for a hypothetical business."
                ],
                "conclusion": [
                    "Present SMART business goals created during the lesson.",
                    "Discuss how goal setting contributes to business success.",
                    "Reflect on personal application of goal-setting principles."
                ],
                "extended": [
                    "Interview a local business owner about their business goals.",
                    "Create a vision board for a dream business with short-term and long-term goals.",
                    "Research on how successful companies set and achieve their goals."
                ]
            },
            "Budgeting in Business": {
                "introduction": [
                    "Teacher presents a simple budget scenario and asks learners to identify its components.",
                    "Brainstorm on the meaning and importance of budgeting in personal finance.",
                    "Show examples of business budgets from real companies."
                ],
                "development": [
                    "Discuss the meaning, importance, and types of business budgets.",
                    "Use digital resources to research types of budgets: sales budget, production budget, cash budget.",
                    "Practice preparing a simple business budget for a school canteen.",
                    "Analyse case studies on how budgeting helps control spending."
                ],
                "conclusion": [
                    "Present prepared budgets to the class for peer review.",
                    "Discuss challenges in preparing and adhering to budgets.",
                    "Summarize key principles of effective budgeting."
                ],
                "extended": [
                    "Create a monthly budget for a small business idea.",
                    "Research digital budgeting tools and applications.",
                    "Interview an accountant about budgeting practices in business."
                ]
            },
            "Banking": {
                "introduction": [
                    "Teacher displays images of banks and financial services and asks learners about their experiences.",
                    "Brainstorm on the role of banks in the economy.",
                    "Show video clips on modern banking services in Kenya including mobile banking."
                ],
                "development": [
                    "Discuss and present the meaning and importance of banking in Kenya's economy.",
                    "Research types of bank accounts: savings, current, fixed deposit, and their features.",
                    "Share experiences on ethical and unethical practices in banking.",
                    "Use digital resources to explore trends in banking: mobile banking, internet banking, agency banking.",
                    "Practice filling forms to open a junior savings account."
                ],
                "conclusion": [
                    "Present findings on types of bank accounts and their suitability.",
                    "Discuss the importance of choosing the right bank and account type.",
                    "Reflect on how banking services benefit individuals and businesses."
                ],
                "extended": [
                    "Visit a bank to learn about their services and products.",
                    "Research on the Central Bank of Kenya and its role.",
                    "Create a comparison chart of different banks and their services."
                ]
            }
        },
        "Business and Its Environment": {
            "Business Activities": {
                "introduction": [
                    "Teacher displays images of various business activities and asks learners to classify them.",
                    "Brainstorm on the differences between needs and wants.",
                    "Show video on how businesses satisfy human wants."
                ],
                "development": [
                    "Discuss and present the meaning and differences between human needs and wants.",
                    "Use resources to research types of economic resources: land, labour, capital, entrepreneurship.",
                    "Brainstorm on scarcity, choice, and opportunity cost with practical examples.",
                    "Role play on classification of business activities: trade, aids to trade, industrial activities.",
                    "Research micro and macro factors affecting business environment."
                ],
                "conclusion": [
                    "Prepare and present a scale of preference for back-to-school needs.",
                    "Discuss how economic resources are used in production.",
                    "Summarize factors affecting business activities."
                ],
                "extended": [
                    "Survey local businesses to identify their activities and challenges.",
                    "Research on a successful Kenyan business and factors contributing to its success.",
                    "Create a poster showing classification of business activities."
                ]
            },
            "Types of Business Ownership": {
                "introduction": [
                    "Teacher displays images of different types of businesses and asks learners to identify ownership types.",
                    "Brainstorm on businesses learners know and their ownership structures.",
                    "Share examples of sole proprietorships, partnerships, and cooperatives in the community."
                ],
                "development": [
                    "Discuss and present on sole proprietorship: formation, management, sources of finance.",
                    "Research partnerships: formation, types, partnership deed, advantages and disadvantages.",
                    "Analyse cooperatives: types, formation, registration, management structure.",
                    "Debate on advantages and disadvantages of each business ownership type.",
                    "Case studies of successful businesses under each ownership type."
                ],
                "conclusion": [
                    "Present comparison charts of different ownership types.",
                    "Discuss factors to consider when choosing a business ownership type.",
                    "Reflect on which ownership type suits different business scenarios."
                ],
                "extended": [
                    "Interview owners of different business types about their experiences.",
                    "Research on companies limited by shares and their structure.",
                    "Visit a cooperative society to learn about their operations."
                ]
            },
            "Entrepreneurship": {
                "introduction": [
                    "Teacher presents stories of successful entrepreneurs and asks learners what makes them successful.",
                    "Brainstorm on the meaning of entrepreneurship and entrepreneurial skills.",
                    "Show videos of young entrepreneurs in Kenya."
                ],
                "development": [
                    "Discuss and present entrepreneurial skills: creativity, risk-taking, decision-making.",
                    "Research types of entrepreneurs: innovative, imitative, fabian, drone.",
                    "Analyse case studies on business ideas and opportunities in Kenya.",
                    "Learn about business incubation and its importance for startups.",
                    "Conduct self-entrepreneurial assessment on personal qualities."
                ],
                "conclusion": [
                    "Present business ideas identified during the lesson.",
                    "Discuss how to evaluate business opportunities.",
                    "Reflect on personal entrepreneurial strengths and areas for improvement."
                ],
                "extended": [
                    "Start a small business venture in school with teacher guidance.",
                    "Research on youth entrepreneurship programs in Kenya.",
                    "Create a simple business plan for a viable business idea."
                ]
            }
        },
        "Government and Global Influence in Business": {
            "Public Finance": {
                "introduction": [
                    "Teacher presents Kenya's budget highlights and asks learners about taxes they know.",
                    "Brainstorm on the meaning and sources of public finance.",
                    "Show video on how taxes are used in national development."
                ],
                "development": [
                    "Discuss and present sources of public finance: taxation, borrowing, grants.",
                    "Research principles of taxation: equity, certainty, convenience, economy.",
                    "Learn about types of taxes: direct and indirect taxes in Kenya.",
                    "Analyse custom duties and their role in international trade.",
                    "Discuss tax compliance requirements: KRA registration, tax returns filing."
                ],
                "conclusion": [
                    "Present an article on the importance of taxation in Kenya.",
                    "Discuss ethical issues in taxation.",
                    "Reflect on citizens' responsibility in tax payment."
                ],
                "extended": [
                    "Research on how government allocates tax revenue.",
                    "Visit KRA offices to learn about tax compliance.",
                    "Create awareness materials on the importance of paying taxes."
                ]
            },
            "International Trade": {
                "introduction": [
                    "Teacher displays products from different countries and asks about trade between nations.",
                    "Brainstorm on goods Kenya exports and imports.",
                    "Show video on international trade and its importance."
                ],
                "development": [
                    "Discuss and present the meaning, types, and importance of international trade.",
                    "Research Kenya's trading partners and major exports/imports.",
                    "Learn about terms of trade: FOB, CIF, balance of trade, balance of payments.",
                    "Explore digital platforms used in international trade.",
                    "Identify local products with export potential."
                ],
                "conclusion": [
                    "Present findings on opportunities in international trade for Kenya.",
                    "Discuss challenges and limitations of international trade.",
                    "Reflect on how to promote Kenyan products in global markets."
                ],
                "extended": [
                    "Research on regional trading blocs Kenya belongs to.",
                    "Interview exporters about their experiences in international trade.",
                    "Create a product proposal for a local product suitable for export."
                ]
            }
        },
        "Financial Records in Business": {
            "Business Transactions": {
                "introduction": [
                    "Teacher presents sample business documents and asks learners to identify them.",
                    "Brainstorm on the meaning and types of business transactions.",
                    "Show examples of cash and credit transactions."
                ],
                "development": [
                    "Discuss and present the meaning and classification of business transactions.",
                    "Practice recording cash and credit transactions.",
                    "Learn the importance of maintaining accurate financial records.",
                    "Analyse case studies on consequences of poor record keeping."
                ],
                "conclusion": [
                    "Present recorded transactions for peer review.",
                    "Discuss the importance of accurate record keeping in business.",
                    "Summarize types of business transactions."
                ],
                "extended": [
                    "Visit a business to observe their record keeping practices.",
                    "Create a simple record keeping system for a school project.",
                    "Research on digital accounting software used in Kenya."
                ]
            },
            "Source Documents and Journals": {
                "introduction": [
                    "Teacher displays various source documents and asks learners to identify them.",
                    "Brainstorm on why businesses keep source documents.",
                    "Show samples of receipts, invoices, and other business documents."
                ],
                "development": [
                    "Identify and describe source documents: receipts, invoices, delivery notes, quotations.",
                    "Learn the uses of different source documents in business.",
                    "Understand books of original entry: sales journal, purchases journal, cash book.",
                    "Practice recording transactions in appropriate journals."
                ],
                "conclusion": [
                    "Present journal entries for review and correction.",
                    "Discuss the flow of information from source documents to journals.",
                    "Summarize the importance of proper documentation."
                ],
                "extended": [
                    "Design source documents for a hypothetical business.",
                    "Research on electronic invoicing and its benefits.",
                    "Create a complete set of business transactions with supporting documents."
                ]
            }
        }
    },
    "Christian Religious Education": {
        "The Old Testament": {
            "The Holy Bible": {
                "introduction": [
                    "Teacher displays the Bible and asks learners to share how they handle the Holy Bible.",
                    "Brainstorm on the meaning of 'inspired' as it relates to the Bible.",
                    "Show a chart of Old Testament book categories."
                ],
                "development": [
                    "Read Psalms 119:160, Isaiah 55:11, Jeremiah 1:9 and discuss Bible as inspired word of God.",
                    "Research human authors who wrote the Bible and their backgrounds.",
                    "Use charts or flash cards to categorise Old Testament books: Law, History, Poetry, Prophets.",
                    "Identify and describe literary forms in the Bible: narrative, poetry, prophecy, law, wisdom.",
                    "Select and creatively present a Psalm through song, drama, or recitation."
                ],
                "conclusion": [
                    "Present posters showing literary forms used in the Bible.",
                    "Discuss why the Bible is considered the inspired word of God.",
                    "Reflect on the importance of the Bible in daily life."
                ],
                "extended": [
                    "Create a personal Bible reading schedule.",
                    "Research on the history of Bible translation into local languages.",
                    "Memorize and present a meaningful passage from the Psalms."
                ]
            },
            "Methods of Studying the Holy Bible": {
                "introduction": [
                    "Teacher asks learners to share their experiences reading the Bible.",
                    "Brainstorm on different methods of studying the Bible.",
                    "Show examples of Bible study guides and concordances."
                ],
                "development": [
                    "Research five methods of studying the Bible: inductive, topical, biographical, devotional, synthetic.",
                    "Interview a pastor or chaplain on benefits of studying the Bible.",
                    "Apply inductive method to study Matthew 13:44-46 and Romans 8:28-32.",
                    "Read the book of Jonah and write his biography.",
                    "Use concordance to search verses on integrity and purity."
                ],
                "conclusion": [
                    "Share insights from applying different Bible study methods.",
                    "Discuss benefits of regular Bible study.",
                    "Commit to daily Bible reading for spiritual growth."
                ],
                "extended": [
                    "Keep a reflection journal on daily Bible readings.",
                    "Research on Bible study apps and digital resources.",
                    "Form a Bible study group with peers."
                ]
            },
            "The Exodus": {
                "introduction": [
                    "Teacher shows images of Egypt and asks about the story of Moses.",
                    "Brainstorm on what learners know about the Exodus.",
                    "Show video clips on the life of Moses."
                ],
                "development": [
                    "Study the early life of Moses in Egypt and Midian.",
                    "Analyse God's call to Moses at the burning bush (Exodus 3).",
                    "Examine the ten plagues and their significance.",
                    "Study the Passover event and its importance in Jewish and Christian tradition.",
                    "Discuss how the Exodus story relates to liberation struggles today."
                ],
                "conclusion": [
                    "Present findings on the significance of Passover.",
                    "Discuss lessons from Moses's response to God's call.",
                    "Reflect on contemporary applications of Exodus themes."
                ],
                "extended": [
                    "Compare the Passover to the Lord's Supper.",
                    "Research on how different communities celebrate freedom from oppression.",
                    "Create a drama presentation on the Exodus story."
                ]
            },
            "The Sinai Covenant": {
                "introduction": [
                    "Teacher asks learners about agreements or covenants they know.",
                    "Brainstorm on the meaning of covenant in biblical context.",
                    "Display the Ten Commandments poster."
                ],
                "development": [
                    "Study the making of the Sinai Covenant (Exodus 19-24).",
                    "Analyse each of the Ten Commandments and their relevance today.",
                    "Discuss how the Israelites broke the covenant (golden calf incident).",
                    "Compare the Sinai Covenant with the New Covenant in Christ.",
                    "Apply covenant principles to relationships and responsibilities."
                ],
                "conclusion": [
                    "Present on the relevance of the Ten Commandments today.",
                    "Discuss what happens when covenants are broken.",
                    "Reflect on personal commitment to God's laws."
                ],
                "extended": [
                    "Research on different covenants in the Bible.",
                    "Create a personal covenant of commitment to moral values.",
                    "Interview community elders on traditional covenants in your culture."
                ]
            }
        },
        "The New Testament": {
            "Infancy and Early Life of Jesus Christ": {
                "introduction": [
                    "Teacher shows nativity scene images and asks about Christmas celebrations.",
                    "Brainstorm on what learners know about Jesus's birth.",
                    "Play carols about the birth of Jesus."
                ],
                "development": [
                    "Study the announcements of births of John the Baptist and Jesus (Luke 1).",
                    "Analyse the circumstances of Jesus's birth in Bethlehem.",
                    "Examine Jesus's presentation in the temple and Simeon's prophecy.",
                    "Study Jesus at the temple at age twelve (Luke 2:41-52).",
                    "Discuss values demonstrated in Jesus's early life: obedience, wisdom, humility."
                ],
                "conclusion": [
                    "Present on lessons from Jesus's childhood.",
                    "Discuss how Mary and Joseph modeled good parenting.",
                    "Reflect on how to emulate values from Jesus's early life."
                ],
                "extended": [
                    "Compare Luke and Matthew's accounts of Jesus's birth.",
                    "Research on cultural context of childbirth in first-century Palestine.",
                    "Create a presentation on the significance of Jesus's birth."
                ]
            },
            "Galilean Ministry": {
                "introduction": [
                    "Teacher displays map of Galilee and asks about Jesus's ministry there.",
                    "Brainstorm on miracles and teachings of Jesus learners know.",
                    "Show video clips on Jesus's miracles."
                ],
                "development": [
                    "Study Jesus's baptism by John and temptation in the wilderness.",
                    "Analyse the calling of the first disciples.",
                    "Examine miracles of Jesus: healing, nature miracles, raising the dead.",
                    "Study key teachings: Sermon on the Mount, parables of the Kingdom.",
                    "Discuss the significance of Jesus's ministry in Galilee."
                ],
                "conclusion": [
                    "Present on lessons from Jesus's Galilean ministry.",
                    "Discuss how Jesus's teachings apply today.",
                    "Reflect on discipleship and following Jesus."
                ],
                "extended": [
                    "Research on the geography and culture of Galilee.",
                    "Create a map showing key locations in Jesus's ministry.",
                    "Dramatize one of Jesus's parables."
                ]
            }
        },
        "Church in Action": {
            "The Holy Spirit": {
                "introduction": [
                    "Teacher asks learners what they know about the Holy Spirit.",
                    "Brainstorm on how the Holy Spirit works in believers' lives.",
                    "Read Acts 2 about the day of Pentecost."
                ],
                "development": [
                    "Study Old Testament references to the Spirit of God.",
                    "Analyse the events of Pentecost in Acts 2.",
                    "Examine the work of the Holy Spirit in the early church.",
                    "Discuss the role of the Holy Spirit in Christian life today.",
                    "Study passages on being filled with the Holy Spirit."
                ],
                "conclusion": [
                    "Present on the work of the Holy Spirit.",
                    "Discuss how to experience the Holy Spirit's power.",
                    "Pray for the guidance of the Holy Spirit."
                ],
                "extended": [
                    "Research on how different churches teach about the Holy Spirit.",
                    "Interview church leaders on experiencing the Holy Spirit.",
                    "Create a presentation on symbols of the Holy Spirit."
                ]
            },
            "Sacraments": {
                "introduction": [
                    "Teacher displays images of baptism and communion and asks about their significance.",
                    "Brainstorm on the meaning of sacraments.",
                    "Show video on church sacraments."
                ],
                "development": [
                    "Study the meaning and significance of sacraments.",
                    "Analyse baptism: its meaning, modes, and importance.",
                    "Examine the Lord's Supper: institution, meaning, practice.",
                    "Compare how different denominations practice sacraments.",
                    "Discuss personal preparation for receiving sacraments."
                ],
                "conclusion": [
                    "Present on the significance of sacraments.",
                    "Discuss how sacraments strengthen faith.",
                    "Reflect on personal experiences with sacraments."
                ],
                "extended": [
                    "Research on additional sacraments in different Christian traditions.",
                    "Interview a pastor about the significance of sacraments.",
                    "Prepare a testimony on the impact of baptism or communion."
                ]
            }
        },
        "Christian Living Today": {
            "Christian Ethics": {
                "introduction": [
                    "Teacher presents ethical dilemmas and asks learners how to respond.",
                    "Brainstorm on the meaning of ethics and morality.",
                    "Discuss contemporary ethical issues facing youth."
                ],
                "development": [
                    "Study the meaning and sources of Christian ethics: Bible, church teaching, reason, experience.",
                    "Analyse ethical issues: abortion, euthanasia, corruption, drug abuse.",
                    "Examine Christian responses to ethical challenges.",
                    "Discuss how to make ethical decisions using biblical principles.",
                    "Role play ethical decision-making scenarios."
                ],
                "conclusion": [
                    "Present on Christian approaches to ethical issues.",
                    "Discuss challenges in living ethically in modern society.",
                    "Commit to ethical living based on Christian principles."
                ],
                "extended": [
                    "Research on bioethics and Christian perspectives.",
                    "Create a guide for ethical decision-making for youth.",
                    "Interview a counselor about ethical issues facing young people."
                ]
            },
            "Human Rights (Non-discrimination)": {
                "introduction": [
                    "Teacher displays Universal Declaration of Human Rights and asks about its content.",
                    "Brainstorm on forms of discrimination in society.",
                    "Show video on human rights and dignity."
                ],
                "development": [
                    "Study the Christian understanding of human dignity (Imago Dei).",
                    "Analyse forms of discrimination: racism, tribalism, gender, disability.",
                    "Examine biblical teachings against discrimination (Galatians 3:28).",
                    "Discuss the church's role in promoting human rights.",
                    "Research on human rights violations and Christian response."
                ],
                "conclusion": [
                    "Present on Christian response to discrimination.",
                    "Discuss how to promote inclusion and equality.",
                    "Commit to respecting human rights in daily life."
                ],
                "extended": [
                    "Research on organizations fighting discrimination.",
                    "Create awareness materials on human rights.",
                    "Organize an activity promoting inclusion in school."
                ]
            }
        }
    },
    "Electrical Technology": {
        "Fundamentals of Electrical Technology": {
            "Introduction to Electrical Technology": {
                "introduction": [
                    "Teacher displays electrical appliances and asks about electricity use in daily life.",
                    "Brainstorm on the importance of electrical technology.",
                    "Show video on careers in electrical technology."
                ],
                "development": [
                    "Discuss the importance of electrical technology in society.",
                    "Research career opportunities: electrician, electrical engineer, electronics technician.",
                    "Study safety regulations and personal protective equipment (PPE).",
                    "Role play safety procedures in an electrical workshop.",
                    "Learn about roles of stakeholders: workers, employers, OSHA, KEBS, ERC."
                ],
                "conclusion": [
                    "Present on career opportunities in electrical technology.",
                    "Demonstrate proper use of PPE.",
                    "Commit to observing safety in all electrical work."
                ],
                "extended": [
                    "Visit an electrical installation workshop.",
                    "Research on electrical accidents and their prevention.",
                    "Create safety posters for the workshop."
                ]
            },
            "D.C Electric Circuit": {
                "introduction": [
                    "Teacher displays a simple circuit and asks learners to identify components.",
                    "Brainstorm on basic electrical quantities: voltage, current, resistance.",
                    "Demonstrate a simple circuit lighting a bulb."
                ],
                "development": [
                    "Study basic electrical quantities and their units.",
                    "Apply Ohm's law (V=IR) in circuit calculations.",
                    "Analyse series and parallel circuit connections.",
                    "Calculate power (P=VI) and energy (E=Pt) in circuits.",
                    "Construct and test simple D.C circuits."
                ],
                "conclusion": [
                    "Present calculations on circuit problems.",
                    "Demonstrate working circuits.",
                    "Discuss practical applications of D.C circuits."
                ],
                "extended": [
                    "Research on Kirchhoff's laws.",
                    "Build a simple circuit project like a torch.",
                    "Calculate electricity consumption of household appliances."
                ]
            },
            "Capacitors and Capacitance": {
                "introduction": [
                    "Teacher displays various capacitors and asks about their use.",
                    "Brainstorm on where capacitors are found in everyday devices.",
                    "Show video on how capacitors work."
                ],
                "development": [
                    "Study the concept of capacitance and its unit (Farad).",
                    "Identify types of capacitors: ceramic, electrolytic, film.",
                    "Calculate equivalent capacitance in series and parallel.",
                    "Conduct experiments on charging and discharging capacitors.",
                    "Discuss applications of capacitors in electronic circuits."
                ],
                "conclusion": [
                    "Present on types and applications of capacitors.",
                    "Demonstrate capacitor calculations.",
                    "Discuss the importance of capacitors in electronics."
                ],
                "extended": [
                    "Research on supercapacitors and their applications.",
                    "Build a simple capacitor using household materials.",
                    "Investigate capacitor failure modes and safety."
                ]
            },
            "Cells and Batteries": {
                "introduction": [
                    "Teacher displays various cells and batteries and asks about their uses.",
                    "Brainstorm on devices that use batteries.",
                    "Show video on how batteries work."
                ],
                "development": [
                    "Study primary and secondary cells and their differences.",
                    "Classify types of batteries: lead-acid, lithium-ion, alkaline.",
                    "Practice connecting cells in series and parallel.",
                    "Learn battery maintenance: charging, storage, disposal.",
                    "Discuss environmental concerns with battery disposal."
                ],
                "conclusion": [
                    "Present on types of batteries and their applications.",
                    "Demonstrate proper battery connection.",
                    "Discuss safe battery handling and disposal."
                ],
                "extended": [
                    "Research on electric vehicle batteries.",
                    "Build a simple lemon battery.",
                    "Investigate battery recycling programs in Kenya."
                ]
            }
        },
        "Electrical Machines": {
            "Magnetism": {
                "introduction": [
                    "Teacher demonstrates magnetic attraction with magnets and asks about magnetism.",
                    "Brainstorm on properties of magnets.",
                    "Show video on Earth's magnetic field."
                ],
                "development": [
                    "Study the concept of magnetism and magnetic materials.",
                    "Investigate properties: attraction, repulsion, magnetic poles.",
                    "Map magnetic field patterns using iron filings.",
                    "Discuss the molecular theory of magnetism.",
                    "Explore applications of magnets in daily life."
                ],
                "conclusion": [
                    "Present findings on magnetic field patterns.",
                    "Demonstrate magnetic properties.",
                    "Discuss importance of magnetism in electrical machines."
                ],
                "extended": [
                    "Research on permanent magnets vs electromagnets.",
                    "Build a simple compass.",
                    "Investigate magnetic storage in computers."
                ]
            },
            "Electromagnetism": {
                "introduction": [
                    "Teacher demonstrates electromagnet and asks about electricity and magnetism relationship.",
                    "Brainstorm on where electromagnets are used.",
                    "Show video on electromagnetic induction."
                ],
                "development": [
                    "Study the relationship between electricity and magnetism.",
                    "Build simple electromagnets and test their strength.",
                    "Explore Faraday's law of electromagnetic induction.",
                    "Discuss applications: motors, generators, transformers.",
                    "Calculate induced EMF in coils."
                ],
                "conclusion": [
                    "Present on applications of electromagnetism.",
                    "Demonstrate working electromagnets.",
                    "Discuss the importance of electromagnetic induction."
                ],
                "extended": [
                    "Research on electromagnetic applications in industry.",
                    "Build a simple electric motor.",
                    "Investigate wireless charging technology."
                ]
            },
            "Measuring Instruments": {
                "introduction": [
                    "Teacher displays multimeter and asks about electrical measurements.",
                    "Brainstorm on what quantities need to be measured in electrical work.",
                    "Demonstrate reading a meter."
                ],
                "development": [
                    "Identify measuring instruments: ammeter, voltmeter, multimeter, wattmeter.",
                    "Study the working principles of moving coil meters.",
                    "Practice using multimeters to measure voltage, current, resistance.",
                    "Learn proper connection of instruments in circuits.",
                    "Interpret meter readings accurately."
                ],
                "conclusion": [
                    "Demonstrate correct use of measuring instruments.",
                    "Present readings from practical measurements.",
                    "Discuss the importance of accurate measurements."
                ],
                "extended": [
                    "Research on digital vs analog meters.",
                    "Practice troubleshooting circuits using a multimeter.",
                    "Investigate industrial measurement systems."
                ]
            }
        },
        "Electrical Installation": {
            "Generation, Transmission and Distribution of Electricity": {
                "introduction": [
                    "Teacher shows diagram of electricity supply chain and asks about power sources.",
                    "Brainstorm on how electricity reaches homes.",
                    "Show video on power generation in Kenya."
                ],
                "development": [
                    "Study methods of electricity generation: hydro, thermal, geothermal, wind, solar.",
                    "Analyse the transmission system: substations, high voltage lines.",
                    "Examine distribution systems: transformers, distribution lines.",
                    "Discuss Kenya's electricity grid and power plants.",
                    "Explore renewable energy sources and their potential."
                ],
                "conclusion": [
                    "Present on Kenya's electricity generation mix.",
                    "Discuss challenges in electricity distribution.",
                    "Reflect on the importance of electricity in development."
                ],
                "extended": [
                    "Research on Kenya Power and rural electrification.",
                    "Visit a power generation plant or substation.",
                    "Investigate smart grid technologies."
                ]
            },
            "Equipment at the Intake Point": {
                "introduction": [
                    "Teacher shows diagram of consumer unit and asks about electrical connection to buildings.",
                    "Brainstorm on equipment seen in home electrical panels.",
                    "Show video on electrical intake installation."
                ],
                "development": [
                    "Identify intake equipment: service cable, meter, consumer unit, MCBs, RCDs.",
                    "Study functions of each component in the intake system.",
                    "Learn about earthing systems and their importance.",
                    "Practice identifying components in a consumer unit.",
                    "Discuss safety features and regulations."
                ],
                "conclusion": [
                    "Present on intake equipment functions.",
                    "Demonstrate identification of components.",
                    "Discuss the importance of proper installation."
                ],
                "extended": [
                    "Research on smart meters and their benefits.",
                    "Investigate common faults in consumer units.",
                    "Study KPLC connection requirements."
                ]
            },
            "Final Circuits": {
                "introduction": [
                    "Teacher shows circuit diagram and asks about lighting and power circuits.",
                    "Brainstorm on electrical circuits in classrooms.",
                    "Demonstrate a simple lighting circuit."
                ],
                "development": [
                    "Study types of final circuits: lighting, power, dedicated circuits.",
                    "Design final circuits for different applications.",
                    "Learn wiring regulations and cable sizing.",
                    "Practice wiring a simple lighting circuit.",
                    "Test and commission circuits using appropriate procedures."
                ],
                "conclusion": [
                    "Present circuit designs.",
                    "Demonstrate working circuits.",
                    "Discuss testing and commissioning procedures."
                ],
                "extended": [
                    "Research on smart home electrical systems.",
                    "Wire a practical project like a lamp holder circuit.",
                    "Investigate energy-efficient lighting solutions."
                ]
            }
        },
        "Electronics": {
            "Semiconductor Theory": {
                "introduction": [
                    "Teacher displays electronic components and asks about semiconductors.",
                    "Brainstorm on materials that conduct electricity.",
                    "Show video on semiconductor manufacturing."
                ],
                "development": [
                    "Study atomic structure and electron behavior.",
                    "Differentiate conductors, insulators, and semiconductors.",
                    "Analyse intrinsic and extrinsic semiconductors.",
                    "Explore doping process: N-type and P-type semiconductors.",
                    "Discuss applications of semiconductors in electronics."
                ],
                "conclusion": [
                    "Present on semiconductor properties.",
                    "Discuss the importance of semiconductors in technology.",
                    "Reflect on semiconductor applications in daily life."
                ],
                "extended": [
                    "Research on silicon chip manufacturing.",
                    "Investigate semiconductor industry in the world.",
                    "Explore future semiconductor technologies."
                ]
            },
            "Semiconductor Diodes": {
                "introduction": [
                    "Teacher displays various diodes and asks about their function.",
                    "Brainstorm on where diodes are used.",
                    "Demonstrate diode forward and reverse bias."
                ],
                "development": [
                    "Study the PN junction and diode operation.",
                    "Identify types of diodes: rectifier, LED, zener, photodiode.",
                    "Test diodes using a multimeter.",
                    "Build simple rectifier circuits: half-wave, full-wave.",
                    "Discuss diode applications in electronic circuits."
                ],
                "conclusion": [
                    "Present on diode types and applications.",
                    "Demonstrate diode testing procedures.",
                    "Discuss the importance of diodes in electronics."
                ],
                "extended": [
                    "Research on LED lighting technology.",
                    "Build a simple power supply using diodes.",
                    "Investigate solar cell operation."
                ]
            },
            "Transistors": {
                "introduction": [
                    "Teacher displays transistors and asks about their function.",
                    "Brainstorm on where transistors are used.",
                    "Show video on transistor invention and impact."
                ],
                "development": [
                    "Study BJT structure: NPN and PNP transistors.",
                    "Understand transistor operation as switch and amplifier.",
                    "Identify transistor terminals: base, collector, emitter.",
                    "Test transistors using a multimeter.",
                    "Build simple transistor circuits: switch, amplifier."
                ],
                "conclusion": [
                    "Present on transistor types and applications.",
                    "Demonstrate transistor testing.",
                    "Discuss transistors in modern electronics."
                ],
                "extended": [
                    "Research on integrated circuits and microprocessors.",
                    "Build a transistor-based project.",
                    "Investigate Moore's Law and transistor development."
                ]
            }
        }
    },
    "Fine Arts": {
        "Picture Making Techniques (2D Art)": {
            "Drawing": {
                "introduction": [
                    "Teacher displays various drawings and asks learners to identify techniques used.",
                    "Brainstorm on elements and principles of art.",
                    "Show examples of perspective drawings."
                ],
                "development": [
                    "Study elements of 2D art: line, shape, texture, value, colour.",
                    "Learn principles of art: balance, dominance, proportion, rhythm, harmony.",
                    "Practice one-point perspective drawing with cubes and buildings.",
                    "Explore two-point perspective for angular objects.",
                    "Execute a still life composition using learned techniques."
                ],
                "conclusion": [
                    "Display drawings for peer critique.",
                    "Discuss how elements and principles enhance artwork.",
                    "Make a portfolio folder to store artworks."
                ],
                "extended": [
                    "Create drawings from observation in the environment.",
                    "Research on famous artists and their drawing techniques.",
                    "Build a portfolio of different drawing styles."
                ]
            },
            "Painting": {
                "introduction": [
                    "Teacher displays paintings and asks about techniques and colours used.",
                    "Brainstorm on colour theory and mixing.",
                    "Demonstrate watercolour and acrylic techniques."
                ],
                "development": [
                    "Study colour theory: primary, secondary, tertiary colours.",
                    "Explore warm and cool colours in composition.",
                    "Practice painting techniques: wash, wet-on-wet, dry brush.",
                    "Create paintings using different media: watercolour, acrylic, oil pastel.",
                    "Analyse paintings from Kenyan and African artists."
                ],
                "conclusion": [
                    "Display paintings for exhibition and critique.",
                    "Discuss colour choices and techniques used.",
                    "Appreciate diverse painting styles and traditions."
                ],
                "extended": [
                    "Research on famous Kenyan painters.",
                    "Create a painting inspired by African themes.",
                    "Visit an art gallery to view paintings."
                ]
            },
            "Collage": {
                "introduction": [
                    "Teacher displays collage artworks and asks about materials used.",
                    "Brainstorm on recyclable materials for collage.",
                    "Show video on collage techniques."
                ],
                "development": [
                    "Study the concept and history of collage as an art form.",
                    "Identify suitable materials: paper, fabric, magazines, natural materials.",
                    "Explore techniques: cutting, tearing, arranging, gluing.",
                    "Create collage artworks with various themes.",
                    "Learn proper finishing and display techniques."
                ],
                "conclusion": [
                    "Display collage works for critique.",
                    "Discuss creative use of materials.",
                    "Appreciate collage as an art form."
                ],
                "extended": [
                    "Create collage from upcycled materials.",
                    "Research on famous collage artists.",
                    "Make a mixed-media artwork combining collage and drawing."
                ]
            }
        },
        "Multimedia Arts (2D Art)": {
            "Graphic Design": {
                "introduction": [
                    "Teacher displays graphic designs (logos, posters) and asks about their purpose.",
                    "Brainstorm on where graphic design is used in daily life.",
                    "Show video on graphic design process."
                ],
                "development": [
                    "Study elements of graphic design: typography, colour, layout, imagery.",
                    "Learn design principles: alignment, contrast, hierarchy, repetition.",
                    "Practice designing simple logos and posters.",
                    "Use digital tools for graphic design if available.",
                    "Analyse effective graphic designs and their impact."
                ],
                "conclusion": [
                    "Present graphic design works for critique.",
                    "Discuss effectiveness of designs.",
                    "Explore career opportunities in graphic design."
                ],
                "extended": [
                    "Design promotional materials for a school event.",
                    "Research on graphic design software.",
                    "Visit a printing press or design studio."
                ]
            },
            "Fabric Decoration: Tie and Dye": {
                "introduction": [
                    "Teacher displays tie and dye fabrics and asks about the technique.",
                    "Brainstorm on traditional fabric decoration methods.",
                    "Show video on tie and dye process."
                ],
                "development": [
                    "Study the history and cultural significance of tie and dye.",
                    "Identify materials: fabric, dyes, rubber bands, string.",
                    "Learn tying techniques: spiral, accordion, scrunch, bullseye.",
                    "Practice creating patterns on fabric.",
                    "Apply proper dyeing and fixing procedures."
                ],
                "conclusion": [
                    "Display tie and dye fabrics.",
                    "Discuss patterns achieved and techniques used.",
                    "Appreciate tie and dye as a cultural art form."
                ],
                "extended": [
                    "Create functional items: t-shirts, bags, scarves.",
                    "Research on tie and dye traditions worldwide.",
                    "Start a small business selling tie and dye products."
                ]
            },
            "Fabric Decoration: Batik": {
                "introduction": [
                    "Teacher displays batik fabrics and asks about the technique.",
                    "Brainstorm on wax-resist dyeing methods.",
                    "Show video on batik making process."
                ],
                "development": [
                    "Study the history and origins of batik.",
                    "Identify materials: fabric, wax, tjanting, dyes.",
                    "Learn design application using wax.",
                    "Practice creating batik patterns.",
                    "Apply dyeing and wax removal procedures."
                ],
                "conclusion": [
                    "Display batik fabrics for critique.",
                    "Discuss designs and techniques used.",
                    "Appreciate batik as a traditional art form."
                ],
                "extended": [
                    "Create batik items for use or sale.",
                    "Research on Indonesian batik traditions.",
                    "Combine batik with other fabric decoration techniques."
                ]
            }
        },
        "Indigenous Crafts (3D Art)": {
            "Pottery": {
                "introduction": [
                    "Teacher displays pottery items and asks about their uses.",
                    "Brainstorm on traditional pottery in Kenya.",
                    "Show video on pottery making."
                ],
                "development": [
                    "Study the history and cultural significance of pottery.",
                    "Identify materials: clay, tools, kiln.",
                    "Learn pottery techniques: pinching, coiling, slab building.",
                    "Practice creating pottery items.",
                    "Explore decoration techniques: incision, impression, painting."
                ],
                "conclusion": [
                    "Display pottery items for critique.",
                    "Discuss techniques and cultural significance.",
                    "Appreciate pottery as an indigenous craft."
                ],
                "extended": [
                    "Visit a pottery studio or traditional potter.",
                    "Research on pottery traditions in different Kenyan communities.",
                    "Create functional pottery items."
                ]
            },
            "Sculpture": {
                "introduction": [
                    "Teacher displays sculptures and asks about materials and techniques.",
                    "Brainstorm on famous sculptures and sculptors.",
                    "Show video on sculpture creation."
                ],
                "development": [
                    "Study types of sculpture: relief, in-the-round, kinetic.",
                    "Identify materials: clay, wood, stone, wire, found objects.",
                    "Learn techniques: modeling, carving, constructing.",
                    "Practice creating sculptures using various materials.",
                    "Explore surface treatment and finishing."
                ],
                "conclusion": [
                    "Display sculptures for critique.",
                    "Discuss themes and techniques.",
                    "Appreciate sculpture as an art form."
                ],
                "extended": [
                    "Research on Kenyan sculptors like Gregory Maloba.",
                    "Create sculpture from recycled materials.",
                    "Visit a sculpture gallery or artist's studio."
                ]
            },
            "Weaving": {
                "introduction": [
                    "Teacher displays woven items and asks about materials and techniques.",
                    "Brainstorm on traditional weaving in Kenya.",
                    "Show video on weaving process."
                ],
                "development": [
                    "Study the history and cultural significance of weaving.",
                    "Identify materials: sisal, raffia, palm leaves, grass.",
                    "Learn weaving techniques: basic weave, coiling, plaiting.",
                    "Practice creating woven items.",
                    "Explore pattern and colour design in weaving."
                ],
                "conclusion": [
                    "Display woven items for critique.",
                    "Discuss techniques and patterns used.",
                    "Appreciate weaving as an indigenous craft."
                ],
                "extended": [
                    "Visit a weaving cooperative or traditional weaver.",
                    "Create functional woven items: baskets, mats.",
                    "Research on weaving traditions in different Kenyan communities."
                ]
            },
            "Jewellery and Ornamentation": {
                "introduction": [
                    "Teacher displays jewellery and asks about materials and significance.",
                    "Brainstorm on traditional African jewellery.",
                    "Show video on jewellery making."
                ],
                "development": [
                    "Study the history and cultural significance of jewellery.",
                    "Identify materials: beads, wire, seeds, shells, recycled materials.",
                    "Learn techniques: beading, wire work, stringing.",
                    "Practice creating jewellery items.",
                    "Explore design and colour coordination."
                ],
                "conclusion": [
                    "Display jewellery for critique.",
                    "Discuss designs and techniques used.",
                    "Appreciate jewellery as a form of cultural expression."
                ],
                "extended": [
                    "Research on Maasai beadwork and other traditions.",
                    "Start a jewellery-making business.",
                    "Create jewellery from upcycled materials."
                ]
            },
            "Art Appreciation": {
                "introduction": [
                    "Teacher displays diverse artworks and asks learners to describe them.",
                    "Brainstorm on what makes art valuable.",
                    "Show video on art criticism."
                ],
                "development": [
                    "Study elements of art criticism: description, analysis, interpretation, judgment.",
                    "Practice critiquing artworks objectively.",
                    "Learn about art history and movements.",
                    "Visit galleries or use digital tours to view art.",
                    "Document and present artworks in portfolios."
                ],
                "conclusion": [
                    "Present art critiques to class.",
                    "Discuss criteria for evaluating art.",
                    "Appreciate diverse art forms and cultural expressions."
                ],
                "extended": [
                    "Research on a specific art movement or artist.",
                    "Curate a school art exhibition.",
                    "Write reviews of artworks visited."
                ]
            }
        }
    },
    "French": {
        "Listening and Speaking": {
            "Informational Listening": {
                "introduction": [
                    "Teacher plays a French audio clip and asks learners to identify the topic.",
                    "Brainstorm on strategies for listening to French.",
                    "Introduce key vocabulary for the listening exercise."
                ],
                "development": [
                    "Listen to recordings on everyday topics: introductions, directions, announcements.",
                    "Practice identifying key information: who, what, where, when.",
                    "Take notes while listening to French audio.",
                    "Complete comprehension exercises based on listening.",
                    "Discuss content in French using simple sentences."
                ],
                "conclusion": [
                    "Share answers to listening comprehension questions.",
                    "Discuss strategies that helped understand the audio.",
                    "Practice vocabulary heard in the recordings."
                ],
                "extended": [
                    "Listen to French radio or podcasts.",
                    "Watch French videos with subtitles.",
                    "Practice listening to native speakers online."
                ]
            },
            "Informative Speaking": {
                "introduction": [
                    "Teacher models self-introduction in French.",
                    "Brainstorm on information to share when introducing oneself.",
                    "Practice greetings and basic expressions."
                ],
                "development": [
                    "Practice introducing oneself: name, age, nationality, likes.",
                    "Learn to describe people, places, and objects in French.",
                    "Practice giving simple instructions in French.",
                    "Role play situations: at school, in a shop, at home.",
                    "Record and listen to own speaking for improvement."
                ],
                "conclusion": [
                    "Present self-introductions to the class.",
                    "Provide peer feedback on pronunciation and fluency.",
                    "Reflect on speaking confidence gained."
                ],
                "extended": [
                    "Record a video introduction in French.",
                    "Practice speaking with French-speaking partners online.",
                    "Participate in French speaking competitions."
                ]
            },
            "Situational Speaking": {
                "introduction": [
                    "Teacher presents dialogue scenarios and asks about appropriate responses.",
                    "Brainstorm on situations requiring French communication.",
                    "Model dialogue in a shop or restaurant."
                ],
                "development": [
                    "Learn expressions for different situations: greetings, requests, apologies.",
                    "Practice dialogues: at the market, restaurant, hotel, school.",
                    "Role play customer-service interactions.",
                    "Learn polite expressions and cultural etiquette.",
                    "Express opinions and preferences in French."
                ],
                "conclusion": [
                    "Perform dialogues for the class.",
                    "Discuss cultural aspects of French communication.",
                    "Reflect on confidence in situational speaking."
                ],
                "extended": [
                    "Create original dialogues for new situations.",
                    "Practice with French language exchange partners.",
                    "Visit French-speaking establishments to practice."
                ]
            }
        },
        "Reading": {
            "Extensive Reading": {
                "introduction": [
                    "Teacher displays French books and magazines and asks about reading habits.",
                    "Brainstorm on benefits of reading in French.",
                    "Introduce a class reader or graded reader."
                ],
                "development": [
                    "Read French texts for enjoyment without translation.",
                    "Keep a reading log of books and articles read.",
                    "Practice reading fluency through repeated reading.",
                    "Build vocabulary by noting new words.",
                    "Discuss stories and articles read."
                ],
                "conclusion": [
                    "Share favourite parts of readings with class.",
                    "Discuss new vocabulary learned.",
                    "Set personal reading goals."
                ],
                "extended": [
                    "Read French children's books or comics.",
                    "Join online French reading communities.",
                    "Subscribe to French language magazines."
                ]
            },
            "Reading for Comprehension": {
                "introduction": [
                    "Teacher presents a short French text and asks about its content.",
                    "Brainstorm on reading strategies.",
                    "Preview vocabulary and text structure."
                ],
                "development": [
                    "Read texts on various themes: daily life, travel, culture.",
                    "Answer comprehension questions: factual and inferential.",
                    "Identify main ideas and supporting details.",
                    "Summarize texts in own words.",
                    "Practice reading aloud for fluency."
                ],
                "conclusion": [
                    "Share answers to comprehension questions.",
                    "Discuss reading strategies used.",
                    "Reflect on understanding improvement."
                ],
                "extended": [
                    "Practice with online French reading exercises.",
                    "Read French news websites.",
                    "Complete reading comprehension worksheets."
                ]
            },
            "Critical Reading": {
                "introduction": [
                    "Teacher presents a French article and asks learners to analyse it.",
                    "Brainstorm on what makes a text persuasive or informative.",
                    "Introduce critical reading skills."
                ],
                "development": [
                    "Analyse author's purpose and intended audience.",
                    "Evaluate information for accuracy and bias.",
                    "Compare different texts on similar topics.",
                    "Form and express opinions about texts.",
                    "Discuss themes and issues raised in readings."
                ],
                "conclusion": [
                    "Present critical analyses of texts.",
                    "Discuss different perspectives on readings.",
                    "Appreciate variety in French written texts."
                ],
                "extended": [
                    "Research current events in French-speaking countries.",
                    "Compare French and English news coverage.",
                    "Write opinion pieces responding to readings."
                ]
            }
        },
        "Writing": {
            "Descriptive Writing": {
                "introduction": [
                    "Teacher shows a picture and asks learners to describe it in French.",
                    "Brainstorm on descriptive vocabulary.",
                    "Review adjectives and their agreement."
                ],
                "development": [
                    "Learn vocabulary for describing people, places, objects.",
                    "Practice using adjectives correctly with gender and number agreement.",
                    "Write descriptions of family members and friends.",
                    "Describe places: home, school, neighbourhood.",
                    "Use sensory details in descriptions."
                ],
                "conclusion": [
                    "Read descriptions to the class.",
                    "Provide peer feedback on descriptive language.",
                    "Revise descriptions based on feedback."
                ],
                "extended": [
                    "Write descriptions of favourite places or people.",
                    "Create a descriptive brochure in French.",
                    "Describe scenes from photographs."
                ]
            },
            "Expository Writing": {
                "introduction": [
                    "Teacher presents a topic and asks learners what they know about it.",
                    "Brainstorm on organizing information.",
                    "Model expository paragraph structure."
                ],
                "development": [
                    "Learn to write introduction, body, and conclusion.",
                    "Practice explaining concepts clearly in French.",
                    "Organize ideas logically with connectors.",
                    "Write short essays on familiar topics.",
                    "Edit and revise writings for clarity."
                ],
                "conclusion": [
                    "Share writings with the class.",
                    "Discuss effective organization strategies.",
                    "Reflect on writing improvement."
                ],
                "extended": [
                    "Write reports on French culture or current events.",
                    "Research and write about a French-speaking country.",
                    "Create informational posters in French."
                ]
            },
            "Persuasive Writing": {
                "introduction": [
                    "Teacher presents an opinion and asks if learners agree or disagree.",
                    "Brainstorm on persuasive techniques.",
                    "Model a persuasive paragraph."
                ],
                "development": [
                    "Learn persuasive language and expressions.",
                    "Practice presenting arguments with supporting reasons.",
                    "Write opinion pieces on relevant topics.",
                    "Use appropriate tone and formal language.",
                    "Counter opposing arguments effectively."
                ],
                "conclusion": [
                    "Present persuasive writings to class.",
                    "Discuss most effective arguments.",
                    "Reflect on persuasive writing skills."
                ],
                "extended": [
                    "Write letters to editors in French.",
                    "Participate in French debate activities.",
                    "Create persuasive advertisements in French."
                ]
            }
        },
        "Grammar": {
            "Pronouns and Conjunctions": {
                "introduction": [
                    "Teacher presents sentences and asks learners to identify pronouns.",
                    "Brainstorm on types of pronouns in French.",
                    "Review subject pronouns."
                ],
                "development": [
                    "Study French pronouns: subject, object, possessive, reflexive.",
                    "Practice replacing nouns with appropriate pronouns.",
                    "Learn conjunctions: et, mais, ou, donc, car.",
                    "Practice combining sentences using conjunctions.",
                    "Complete exercises on pronouns and conjunctions."
                ],
                "conclusion": [
                    "Review answers to grammar exercises.",
                    "Discuss common errors and corrections.",
                    "Apply grammar rules in writing exercises."
                ],
                "extended": [
                    "Complete online grammar exercises.",
                    "Use pronouns and conjunctions in creative writing.",
                    "Practice with grammar workbooks."
                ]
            },
            "Prepositions and Adjectives": {
                "introduction": [
                    "Teacher presents sentences and asks about word positions.",
                    "Brainstorm on French prepositions.",
                    "Review adjective agreement rules."
                ],
                "development": [
                    "Study common prepositions: à, de, en, dans, sur, sous.",
                    "Practice using prepositions with places and time.",
                    "Review adjective agreement: gender and number.",
                    "Learn adjective placement rules in French.",
                    "Complete exercises on prepositions and adjectives."
                ],
                "conclusion": [
                    "Review grammar exercise answers.",
                    "Discuss challenging aspects of adjective agreement.",
                    "Apply rules in sentence construction."
                ],
                "extended": [
                    "Practice with interactive grammar tools.",
                    "Create sentences describing locations.",
                    "Write paragraphs using varied adjectives."
                ]
            },
            "Verbs and Negation": {
                "introduction": [
                    "Teacher presents sentences and asks about verb forms.",
                    "Brainstorm on French verb tenses.",
                    "Review regular verb conjugation."
                ],
                "development": [
                    "Study verb conjugation: present, past (passé composé), future.",
                    "Practice conjugating regular -er, -ir, -re verbs.",
                    "Learn common irregular verbs: être, avoir, aller, faire.",
                    "Study negation: ne...pas, ne...jamais, ne...rien.",
                    "Practice forming negative sentences."
                ],
                "conclusion": [
                    "Review verb conjugation exercises.",
                    "Practice negative sentence construction.",
                    "Apply verb forms in conversation."
                ],
                "extended": [
                    "Use verb conjugation apps for practice.",
                    "Write diary entries using various tenses.",
                    "Complete verb conjugation challenges."
                ]
            },
            "Articles and Nouns": {
                "introduction": [
                    "Teacher presents nouns and asks about their articles.",
                    "Brainstorm on article types in French.",
                    "Review noun gender rules."
                ],
                "development": [
                    "Study definite articles: le, la, l', les.",
                    "Learn indefinite articles: un, une, des.",
                    "Practice partitive articles: du, de la, de l', des.",
                    "Study rules for noun gender and common patterns.",
                    "Practice forming plural nouns."
                ],
                "conclusion": [
                    "Review article usage exercises.",
                    "Discuss strategies for remembering noun gender.",
                    "Apply article rules in sentence construction."
                ],
                "extended": [
                    "Create flashcards for noun gender practice.",
                    "Use language apps to reinforce article usage.",
                    "Write shopping lists using correct articles."
                ]
            }
        }
    }
}


async def get_substrand_id(subject_name, strand_name, substrand_name):
    """Get substrand ID by navigating through the hierarchy"""
    subject = await db.subjects.find_one({"name": subject_name})
    if not subject:
        return None
    
    strand = await db.strands.find_one({
        "name": {"$regex": strand_name, "$options": "i"},
        "subjectId": str(subject["_id"])
    })
    if not strand:
        return None
    
    substrand = await db.substrands.find_one({
        "name": {"$regex": substrand_name, "$options": "i"},
        "strandId": str(strand["_id"])
    })
    if substrand:
        return str(substrand["_id"])
    return None


async def seed_activities():
    """Seed learning activities for all 5 new subjects"""
    print("=" * 70)
    print("SEEDING LEARNING ACTIVITIES FOR 5 NEW SUBJECTS")
    print("=" * 70)
    
    activities_added = 0
    activities_updated = 0
    not_found = 0
    
    for subject_name, strands in ACTIVITIES_DATA.items():
        print(f"\n--- Processing {subject_name} ---")
        
        for strand_name, substrands in strands.items():
            for substrand_name, activity_data in substrands.items():
                substrand_id = await get_substrand_id(subject_name, strand_name, substrand_name)
                
                if not substrand_id:
                    print(f"  [SKIP] Substrand not found: {subject_name} > {strand_name} > {substrand_name}")
                    not_found += 1
                    continue
                
                # Check if activities already exist
                existing = await db.learning_activities.find_one({"substrandId": substrand_id})
                
                activity_doc = {
                    "substrandId": substrand_id,
                    "introduction_activities": activity_data.get("introduction", []),
                    "development_activities": activity_data.get("development", []),
                    "conclusion_activities": activity_data.get("conclusion", []),
                    "extended_activities": activity_data.get("extended", [])
                }
                
                if existing:
                    await db.learning_activities.update_one(
                        {"_id": existing["_id"]},
                        {"$set": activity_doc}
                    )
                    activities_updated += 1
                    print(f"  [UPDATE] {substrand_name}")
                else:
                    await db.learning_activities.insert_one(activity_doc)
                    activities_added += 1
                    print(f"  [ADD] {substrand_name}")
    
    print("\n" + "=" * 70)
    print("ACTIVITIES SEEDING COMPLETE")
    print("=" * 70)
    print(f"Activities Added: {activities_added}")
    print(f"Activities Updated: {activities_updated}")
    print(f"Substrands Not Found: {not_found}")
    
    # Verify totals
    total_activities = await db.learning_activities.count_documents({})
    print(f"\nTotal activities in database: {total_activities}")


if __name__ == "__main__":
    asyncio.run(seed_activities())
