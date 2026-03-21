"""LLM-based answer generation service.

Priority:
1. Gemini API  — direct HTTP via urllib (no package needed)
2. Claude API  — direct HTTP via urllib (no package needed)
3. Offline KB  — built-in knowledge base (covers 30+ school topics)
4. Offline ctx — extract best sentences from retrieved chunks
"""

import json
import re
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

from app.utils.helpers import setup_logger
from app.config import LLM_PROVIDER, LLM_API_KEY, LLM_MODEL, LLM_TEMPERATURE

logger = setup_logger(__name__)

# ── Offline Knowledge Base — Class 6-10 NCERT topics ─────────────────────
OFFLINE_KB: Dict[str, Dict[str, str]] = {

    # ── Matter & Substances ───────────────────────────────────────────────
    "matter": {
        "en_simple": "Matter is anything that has mass and occupies space. Everything around us — air, water, rocks — is matter. It exists in three states: solid, liquid, and gas.",
        "en_detailed": "Matter is made of atoms and molecules. In solids, particles are tightly packed and vibrate in place. In liquids, particles flow. In gases, particles move freely. Heating causes matter to change state (e.g., ice → water → steam).",
        "hi_simple": "पदार्थ वह है जिसका द्रव्यमान हो और जो स्थान घेरे। यह ठोस, द्रव और गैस तीन अवस्थाओं में पाया जाता है।",
        "hi_detailed": "पदार्थ परमाणुओं और अणुओं से बना है। ठोस में कण कसे, द्रव में ढीले और गैस में स्वतंत्र होते हैं। गर्म करने पर अवस्था बदलती है।",
        "chapter": "Chapter 1: Matter in Our Surroundings",
    },
    "diffusion": {
        "en_simple": "Diffusion is the process by which particles of a substance spread from a region of high concentration to a region of low concentration. Example: when you spray perfume, the smell spreads throughout the room — that is diffusion.",
        "en_detailed": "Diffusion occurs because particles are always in motion. They move from where they are more concentrated to where they are less concentrated until evenly spread. Diffusion happens in gases (fastest), liquids, and solids (slowest). Temperature increases diffusion rate. Examples: food coloring spreading in water, oxygen entering blood from lungs.",
        "hi_simple": "विसरण वह प्रक्रिया है जिसमें पदार्थ के कण अधिक सांद्रता से कम सांद्रता वाले क्षेत्र की ओर फैलते हैं। उदाहरण: इत्र छिड़कने पर उसकी खुशबू पूरे कमरे में फैल जाती है।",
        "hi_detailed": "विसरण कणों की गति के कारण होता है। गैसों में सबसे तेज, द्रवों में मध्यम और ठोस में सबसे धीमा होता है। तापमान बढ़ने से विसरण की दर बढ़ती है। उदाहरण: पानी में रंग का फैलना, फेफड़ों से रक्त में ऑक्सीजन का जाना।",
        "chapter": "Chapter 1: Matter in Our Surroundings",
    },
    "evaporation": {
        "en_simple": "Evaporation is the process where a liquid changes into gas (vapour) at the surface, below its boiling point. Example: wet clothes dry in sunlight because water evaporates.",
        "en_detailed": "Evaporation happens at the liquid surface. Factors that increase evaporation: higher temperature, more surface area, lower humidity, wind. Evaporation causes cooling — that is why sweating cools your body. It is different from boiling, which happens throughout the liquid.",
        "hi_simple": "वाष्पीकरण वह प्रक्रिया है जिसमें द्रव अपने क्वथनांक से नीचे गैस में बदलता है। उदाहरण: धूप में गीले कपड़े सूख जाते हैं।",
        "hi_detailed": "वाष्पीकरण द्रव की सतह पर होता है। तापमान, सतह क्षेत्र और हवा से दर बढ़ती है। वाष्पीकरण से ठंडक होती है — इसीलिए पसीना शरीर को ठंडा रखता है।",
        "chapter": "Chapter 1: Matter in Our Surroundings",
    },
    "solution": {
        "en_simple": "A solution is a homogeneous mixture of two or more substances. The substance that dissolves is the solute, and the substance in which it dissolves is the solvent. Example: salt dissolved in water.",
        "en_detailed": "Solutions can be solid, liquid, or gas. Concentration = amount of solute per unit volume. A saturated solution cannot dissolve more solute at a given temperature. Solubility increases with temperature for most solids but decreases for gases.",
        "hi_simple": "विलयन दो या अधिक पदार्थों का समांग मिश्रण है। जो घुलता है वह विलेय और जिसमें घुलता है वह विलायक है। उदाहरण: पानी में नमक।",
        "hi_detailed": "विलयन ठोस, द्रव या गैस हो सकते हैं। संतृप्त विलयन में और विलेय नहीं घुल सकता। अधिकांश ठोसों की विलेयता तापमान बढ़ने से बढ़ती है।",
        "chapter": "Chapter 2: Is Matter Around Us Pure?",
    },
    "atom": {
        "en_simple": "An atom is the smallest particle of an element. It has a nucleus containing protons and neutrons, surrounded by electrons moving in shells.",
        "en_detailed": "Atomic number = number of protons = number of electrons (in neutral atom). Mass number = protons + neutrons. Isotopes have same protons but different neutrons. Ions are atoms that have gained or lost electrons.",
        "hi_simple": "परमाणु किसी तत्व का सबसे छोटा कण है। केंद्रक में प्रोटॉन और न्यूट्रॉन होते हैं और चारों ओर इलेक्ट्रॉन घूमते हैं।",
        "hi_detailed": "परमाणु क्रमांक = प्रोटॉनों की संख्या। द्रव्यमान संख्या = प्रोटॉन + न्यूट्रॉन। समस्थानिक: समान प्रोटॉन, भिन्न न्यूट्रॉन। आयन: इलेक्ट्रॉन प्राप्त/खोए हुए परमाणु।",
        "chapter": "Chapter 4: Atoms and Molecules",
    },
    "molecule": {
        "en_simple": "A molecule is the smallest particle of a substance that can exist independently and still show the properties of that substance. It is made of two or more atoms bonded together.",
        "en_detailed": "Molecules can be homoatomic (same atoms, e.g., O₂, H₂) or heteroatomic (different atoms, e.g., H₂O, CO₂). The number of atoms in a molecule is its atomicity. Molecular mass = sum of atomic masses of all atoms.",
        "hi_simple": "अणु किसी पदार्थ का सबसे छोटा स्वतंत्र कण है जो उस पदार्थ के गुण दर्शाता है। यह दो या अधिक परमाणुओं से बना होता है।",
        "hi_detailed": "समपरमाणुक अणु: एक ही तत्व के परमाणु (जैसे O₂, H₂)। विषमपरमाणुक: भिन्न तत्वों के (जैसे H₂O, CO₂)। अणु द्रव्यमान = सभी परमाणु द्रव्यमानों का योग।",
        "chapter": "Chapter 4: Atoms and Molecules",
    },

    # ── Biology ───────────────────────────────────────────────────────────
    "cell": {
        "en_simple": "A cell is the basic unit of life. Every living organism is made of cells. It has a cell membrane, cytoplasm, and a nucleus containing DNA.",
        "en_detailed": "Animal cells: membrane, cytoplasm, nucleus, mitochondria, ribosomes. Plant cells additionally have: cell wall (rigid support), chloroplasts (photosynthesis), large central vacuole. Prokaryotic cells (bacteria) have no nucleus.",
        "hi_simple": "कोशिका जीवन की मूल इकाई है। हर जीव कोशिकाओं से बना है। इसमें कोशिका झिल्ली, कोशिका द्रव्य और केंद्रक होते हैं।",
        "hi_detailed": "जंतु कोशिका: झिल्ली, केंद्रक, माइटोकॉन्ड्रिया, राइबोसोम। पादप कोशिका में अतिरिक्त: कोशिका भित्ति, हरित लवक, रिक्तिका।",
        "chapter": "Chapter 5: The Fundamental Unit of Life",
    },
    "photosynthesis": {
        "en_simple": "Photosynthesis is how plants make food. They use sunlight, water, and carbon dioxide to produce glucose and oxygen.",
        "en_detailed": "Occurs in chloroplasts. Light-dependent stage: sunlight splits water → O₂ released, ATP formed. Calvin cycle: CO₂ fixed into glucose. Equation: 6CO₂ + 6H₂O + light → C₆H₁₂O₆ + 6O₂.",
        "hi_simple": "प्रकाश संश्लेषण में पौधे सूर्य प्रकाश, पानी और CO₂ से ग्लूकोज और ऑक्सीजन बनाते हैं।",
        "hi_detailed": "क्लोरोप्लास्ट में होता है। प्रकाश पानी तोड़ता है → O₂ + ऊर्जा। केल्विन चक्र में CO₂ से ग्लूकोज। सूत्र: 6CO₂+6H₂O+प्रकाश → C₆H₁₂O₆+6O₂।",
        "chapter": "Chapter 6: Life Processes",
    },
    "respiration": {
        "en_simple": "Respiration is the process by which cells break down glucose to release energy. In aerobic respiration, oxygen is used and CO₂ and water are released.",
        "en_detailed": "Aerobic: C₆H₁₂O₆ + 6O₂ → 6CO₂ + 6H₂O + energy (ATP). Anaerobic (no oxygen): glucose → lactic acid (in muscles) or ethanol + CO₂ (in yeast). Aerobic gives more energy. Breathing brings oxygen in; respiration uses it at the cellular level.",
        "hi_simple": "श्वसन में कोशिकाएँ ग्लूकोज को तोड़कर ऊर्जा (ATP) बनाती हैं। वायवीय श्वसन में O₂ लगती है और CO₂ व पानी निकलते हैं।",
        "hi_detailed": "वायवीय: C₆H₁₂O₆+6O₂ → 6CO₂+6H₂O+ऊर्जा। अवायवीय (O₂ के बिना): लैक्टिक एसिड (मांसपेशियों) या इथेनॉल+CO₂ (यीस्ट)।",
        "chapter": "Chapter 6: Life Processes",
    },
    "osmosis": {
        "en_simple": "Osmosis is the movement of water molecules from a region of higher water concentration (low solute) to a region of lower water concentration (high solute) through a semi-permeable membrane.",
        "en_detailed": "Osmosis is a special type of diffusion for water. If a cell is placed in a hypotonic solution (more water outside), water enters → cell swells. In a hypertonic solution (less water outside), water leaves → cell shrinks (plasmolysis in plants). Isotonic: no net movement.",
        "hi_simple": "परासरण में जल अणु अर्ध-पारगम्य झिल्ली के आर-पार अधिक जल सांद्रता से कम जल सांद्रता की ओर जाते हैं।",
        "hi_detailed": "हाइपोटोनिक विलयन में जल कोशिका में जाता है → कोशिका फूलती है। हाइपरटोनिक में जल बाहर जाता है → कोशिका सिकुड़ती है (प्लाज्मोलिसिस)।",
        "chapter": "Chapter 6: Life Processes",
    },
    "tissue": {
        "en_simple": "A tissue is a group of similar cells that work together to perform a specific function. Example: muscle tissue helps in movement; nerve tissue carries signals.",
        "en_detailed": "Plant tissues: meristematic (dividing cells) and permanent (protective, ground, vascular). Animal tissues: epithelial (covering), connective (bone, blood), muscular (movement), nervous (signalling).",
        "hi_simple": "ऊतक समान कोशिकाओं का समूह है जो एक विशेष कार्य करता है। उदाहरण: पेशी ऊतक गति करता है।",
        "hi_detailed": "पादप ऊतक: विभज्योतक और स्थायी। जंतु ऊतक: उपकला, संयोजी (हड्डी, रक्त), पेशीय, तंत्रिका।",
        "chapter": "Chapter 6: Tissues",
    },

    # ── Physics ───────────────────────────────────────────────────────────
    "force": {
        "en_simple": "Force is a push or a pull. It can make an object move, stop, speed up, slow down, or change direction. Force is measured in Newtons (N).",
        "en_detailed": "Newton's 3 laws: (1) Inertia — object stays at rest/motion unless a net force acts. (2) F = ma — force equals mass times acceleration. (3) Every action has an equal and opposite reaction.",
        "hi_simple": "बल धक्का या खिंचाव है। यह वस्तु को चला, रोक, गति बदल या दिशा बदल सकता है। इकाई न्यूटन (N) है।",
        "hi_detailed": "न्यूटन के तीन नियम: (1) जड़त्व (2) F=ma (3) क्रिया-प्रतिक्रिया।",
        "chapter": "Chapter 9: Force and Laws of Motion",
    },
    "friction": {
        "en_simple": "Friction is a force that opposes the relative motion between two surfaces in contact. Rough surfaces have more friction than smooth ones.",
        "en_detailed": "Types: static (prevents motion starting), kinetic (during sliding), rolling (smallest, when object rolls), fluid (in water/air). Friction force = μ × Normal force. Lubricants like oil reduce friction.",
        "hi_simple": "घर्षण दो सतहों के बीच सापेक्ष गति का विरोध करता है। खुरदरी सतहों पर अधिक घर्षण।",
        "hi_detailed": "प्रकार: स्थैतिक, गतिज, लोटनिक (न्यूनतम), तरल। F=μN। स्नेहक घर्षण कम करते हैं।",
        "chapter": "Chapter 12: Friction",
    },
    "gravity": {
        "en_simple": "Gravity is a force that attracts objects toward each other. Earth's gravity pulls everything downward. Weight = mass × g, where g ≈ 9.8 m/s².",
        "en_detailed": "Universal law: F = Gm₁m₂/r². G = 6.674×10⁻¹¹ N·m²/kg². Gravity holds planets in orbit around the Sun. Free fall: all objects fall at same acceleration (ignoring air resistance).",
        "hi_simple": "गुरुत्वाकर्षण वस्तुओं को एक-दूसरे की ओर खींचता है। पृथ्वी पर g≈9.8 m/s²। भार = द्रव्यमान × g।",
        "hi_detailed": "F = Gm₁m₂/r²। गुरुत्वाकर्षण ग्रहों को कक्षा में रखता है। मुक्त पतन में सभी वस्तुएँ समान त्वरण से गिरती हैं।",
        "chapter": "Chapter 10: Gravitation",
    },
    "pressure": {
        "en_simple": "Pressure is force per unit area (P = F/A). A smaller area means more pressure for the same force. Measured in Pascals (Pa). Example: a sharp knife cuts better than a blunt one.",
        "en_detailed": "Fluid pressure increases with depth: P = ρgh. Pascal's law: pressure in a closed fluid transmits equally in all directions (basis of hydraulic systems). Atmospheric pressure at sea level ≈ 101,325 Pa.",
        "hi_simple": "दाब = बल ÷ क्षेत्रफल। छोटे क्षेत्रफल पर अधिक दाब। इकाई पास्कल (Pa)।",
        "hi_detailed": "द्रव में दाब: P = ρgh। पास्कल का नियम: दाब सभी दिशाओं में समान रूप से संचारित होता है। हाइड्रोलिक ब्रेक इसी पर काम करते हैं।",
        "chapter": "Chapter 11: Force and Pressure",
    },
    "sound": {
        "en_simple": "Sound is energy produced by vibrating objects and travels as longitudinal waves through solids, liquids, and gases. It cannot travel through vacuum. Speed in air ≈ 343 m/s.",
        "en_detailed": "Properties: frequency (Hz, pitch), amplitude (loudness, dB), wavelength. Human hearing: 20–20,000 Hz. Ultrasound (>20,000 Hz) used in sonography. Doppler effect: pitch changes when source moves.",
        "hi_simple": "ध्वनि कंपन से उत्पन्न ऊर्जा है। यह अनुदैर्ध्य तरंगों के रूप में ठोस/द्रव/गैस में चलती है, निर्वात में नहीं। हवा में गति ≈343 m/s।",
        "hi_detailed": "गुण: आवृत्ति (Hz, तारत्व), आयाम (dB, तीव्रता)। श्रव्यता: 20–20,000 Hz। पराध्वनि चिकित्सा में उपयोगी।",
        "chapter": "Chapter 12: Sound",
    },
    "light": {
        "en_simple": "Light is an electromagnetic wave that travels at 3×10⁸ m/s in vacuum. It travels in straight lines, can be reflected and refracted. White light splits into 7 colours (VIBGYOR) through a prism.",
        "en_detailed": "Reflection law: angle of incidence = angle of reflection. Refraction: Snell's law n₁sinθ₁ = n₂sinθ₂. Total internal reflection → optical fibre, diamond sparkle. Convex lens converges; concave lens diverges.",
        "hi_simple": "प्रकाश निर्वात में 3×10⁸ m/s से सीधी रेखा में चलता है। यह परावर्तित और अपवर्तित होता है। प्रिज्म से 7 रंगों में बँटता है।",
        "hi_detailed": "परावर्तन: आपतन कोण = परावर्तन कोण। अपवर्तन: n₁sinθ₁=n₂sinθ₂। पूर्ण आंतरिक परावर्तन → ऑप्टिकल फाइबर।",
        "chapter": "Chapter 16: Light",
    },
    "electricity": {
        "en_simple": "Electricity is the flow of electric charges (electrons) through a conductor. Current (I) is measured in Amperes, voltage (V) in Volts, and resistance (R) in Ohms.",
        "en_detailed": "Ohm's law: V = IR. Series circuit: same current, voltages add up. Parallel circuit: same voltage, currents add up. Power = V × I = I²R. Electric energy = Power × time.",
        "hi_simple": "विद्युत आवेश (इलेक्ट्रॉन) का प्रवाह है। धारा (A), वोल्टेज (V), प्रतिरोध (Ω) में मापी जाती है।",
        "hi_detailed": "ओम का नियम: V = IR। श्रेणी परिपथ: धारा समान, वोल्टेज जुड़ते हैं। समानांतर: वोल्टेज समान, धाराएँ जुड़ती हैं।",
        "chapter": "Chapter 12: Electricity",
    },
    "magnetism": {
        "en_simple": "A magnet attracts iron and has two poles: North and South. Like poles repel, unlike poles attract. Earth itself is a giant magnet.",
        "en_detailed": "Magnetic field lines go from North to South outside the magnet. An electromagnet is a temporary magnet created by electric current. A compass needle aligns with Earth's magnetic field. Fleming's left-hand rule gives direction of force on a current-carrying conductor in a magnetic field.",
        "hi_simple": "चुम्बक लोहे को खींचता है और उसके दो ध्रुव होते हैं: उत्तर और दक्षिण। समान ध्रुव प्रतिकर्षित, विपरीत आकर्षित होते हैं।",
        "hi_detailed": "चुम्बकीय क्षेत्र रेखाएँ उत्तर से दक्षिण ध्रुव की ओर जाती हैं। विद्युत चुम्बक अस्थायी होता है। पृथ्वी एक विशाल चुम्बक है।",
        "chapter": "Chapter 13: Magnetic Effects of Electric Current",
    },

    # ── Chemistry ─────────────────────────────────────────────────────────
    "acid": {
        "en_simple": "Acids are substances that taste sour and turn blue litmus paper red. They release H⁺ ions in water. Examples: hydrochloric acid (HCl), sulphuric acid (H₂SO₄), citric acid (in lemons).",
        "en_detailed": "Strong acids (HCl, H₂SO₄) completely ionise in water. Weak acids (acetic acid, carbonic acid) partially ionise. pH < 7 = acidic. Acids react with metals to produce hydrogen gas, with bases to produce salt and water (neutralisation).",
        "hi_simple": "अम्ल खट्टे होते हैं और नीले लिटमस को लाल करते हैं। ये पानी में H⁺ आयन देते हैं। उदाहरण: HCl, H₂SO₄, नींबू में साइट्रिक एसिड।",
        "hi_detailed": "प्रबल अम्ल (HCl, H₂SO₄) पूरी तरह आयनित होते हैं। दुर्बल अम्ल आंशिक। pH<7 = अम्लीय। अम्ल + धातु → H₂ गैस। अम्ल + क्षार → लवण + पानी।",
        "chapter": "Chapter 2: Acids, Bases and Salts",
    },
    "base": {
        "en_simple": "Bases are substances that taste bitter, feel soapy, and turn red litmus paper blue. They release OH⁻ ions in water. Examples: sodium hydroxide (NaOH), calcium hydroxide (Ca(OH)₂).",
        "en_detailed": "Strong bases (NaOH, KOH) fully dissociate. Weak bases (NH₄OH) partially. pH > 7 = basic/alkaline. Bases react with acids in neutralisation to form salt and water. Alkalis are bases that are soluble in water.",
        "hi_simple": "क्षार कड़वे और चिकने होते हैं। ये लाल लिटमस को नीला करते हैं और OH⁻ आयन देते हैं। उदाहरण: NaOH, Ca(OH)₂।",
        "hi_detailed": "pH>7 = क्षारीय। प्रबल क्षार पूरी तरह आयनित। क्षार + अम्ल → लवण + पानी (उदासीनीकरण)। जल में घुलनशील क्षार को क्षारक कहते हैं।",
        "chapter": "Chapter 2: Acids, Bases and Salts",
    },
    "chemical reaction": {
        "en_simple": "A chemical reaction is a process where reactants are transformed into new substances called products. Signs of a chemical reaction: change in colour, gas produced, heat released, precipitate formed.",
        "en_detailed": "Types: combination (A+B→AB), decomposition (AB→A+B), displacement (A+BC→AC+B), double displacement, combustion. Law of conservation of mass: total mass of reactants = total mass of products.",
        "hi_simple": "रासायनिक अभिक्रिया में अभिकारक नए पदार्थ (उत्पाद) में बदलते हैं। संकेत: रंग बदलना, गैस निकलना, ऊष्मा मुक्त होना, अवक्षेप बनना।",
        "hi_detailed": "प्रकार: संयोजन, अपघटन, विस्थापन, द्विविस्थापन, दहन। द्रव्यमान संरक्षण का नियम: अभिकारकों का कुल द्रव्यमान = उत्पादों का कुल द्रव्यमान।",
        "chapter": "Chapter 1: Chemical Reactions and Equations",
    },

    # ── Mathematics ───────────────────────────────────────────────────────
    "algebra": {
        "en_simple": "Algebra uses letters to represent unknown numbers. To solve x + 5 = 12, subtract 5 from both sides: x = 7.",
        "en_detailed": "Key steps: simplify both sides, move variables to one side, move constants to the other, divide by the coefficient. Example: 2x+3=11 → 2x=8 → x=4.",
        "hi_simple": "बीजगणित में अज्ञात को अक्षर से दर्शाते हैं। x+5=12 में x=7।",
        "hi_detailed": "हल: सरल करें → चर एक तरफ → अचर दूसरी तरफ → गुणांक से भाग दें।",
        "chapter": "Chapter 4: Simple Equations",
    },
    "triangle": {
        "en_simple": "A triangle has 3 sides and 3 angles. The sum of all interior angles is always 180°. Pythagorean theorem for right triangles: a² + b² = c².",
        "en_detailed": "Types: equilateral (all equal), isosceles (two equal), scalene (all different). Area = ½ × base × height. Congruence criteria: SSS, SAS, ASA, RHS. Similarity: AA, SSS, SAS.",
        "hi_simple": "त्रिभुज में 3 भुजाएँ और 3 कोण होते हैं। आंतरिक कोणों का योग 180° होता है। a²+b²=c² (समकोण त्रिभुज)।",
        "hi_detailed": "प्रकार: समबाहु, समद्विबाहु, विषमबाहु। क्षेत्रफल=½×आधार×ऊँचाई। सर्वांगसमता: SSS, SAS, ASA।",
        "chapter": "Chapter 6: Triangles",
    },
    "fraction": {
        "en_simple": "A fraction represents part of a whole (numerator/denominator). To add fractions with different denominators, find the LCM first. Example: ½ + ⅓ = 3/6 + 2/6 = 5/6.",
        "en_detailed": "Types: proper (num<den), improper (num≥den), mixed. Multiply: multiply numerators and denominators. Divide: multiply by the reciprocal. Equivalent fractions represent the same value.",
        "hi_simple": "भिन्न पूर्ण के भाग को दर्शाती है। भिन्न जोड़ने के लिए LCM लें। ½+⅓ = 5/6।",
        "hi_detailed": "प्रकार: उचित, अनुचित, मिश्रित। गुणा: अंश×अंश, हर×हर। भाग: व्युत्क्रम लेकर गुणा।",
        "chapter": "Chapter 2: Fractions and Decimals",
    },

    # ── Environment & Geography ───────────────────────────────────────────
    "ecosystem": {
        "en_simple": "An ecosystem is a community of living organisms (plants, animals, bacteria) interacting with their non-living environment (air, water, soil). Example: a forest, a pond, a desert.",
        "en_detailed": "Components: biotic (living — producers, consumers, decomposers) and abiotic (non-living — sunlight, water, temperature). Energy flows through food chains. Nutrients cycle (carbon cycle, nitrogen cycle).",
        "hi_simple": "पारितंत्र में जीवित (पौधे, जंतु, जीवाणु) और अजीवित (वायु, जल, मिट्टी) घटक परस्पर क्रिया करते हैं। उदाहरण: वन, तालाब।",
        "hi_detailed": "जैविक घटक: उत्पादक, उपभोक्ता, अपघटक। अजैविक: सूर्य प्रकाश, जल, तापमान। ऊर्जा खाद्य श्रृंखला में प्रवाहित होती है।",
        "chapter": "Chapter 15: Our Environment",
    },
    "food chain": {
        "en_simple": "A food chain shows the feeding relationships between organisms — who eats whom. It starts with a producer (plant) and ends with a top consumer. Example: grass → grasshopper → frog → snake → eagle.",
        "en_detailed": "Energy decreases at each trophic level (only ~10% passed on). Producers make food via photosynthesis. Herbivores eat plants (primary consumers). Carnivores eat animals. Decomposers break down dead matter.",
        "hi_simple": "खाद्य श्रृंखला दर्शाती है कि कौन किसे खाता है। यह उत्पादक (पौधे) से शुरू होती है। उदाहरण: घास → टिड्डा → मेंढक → साँप → चील।",
        "hi_detailed": "हर पोषी स्तर पर ऊर्जा घटती है (केवल ~10% आगे जाती है)। अपघटक मृत पदार्थ को तोड़ते हैं।",
        "chapter": "Chapter 15: Our Environment",
    },
}


def _find_offline_answer(question: str, language: str) -> Optional[Dict[str, Any]]:
    """Find best matching answer from offline KB using keyword scoring."""
    q = question.lower()
    best_key, best_score = None, 0

    for key in OFFLINE_KB:
        # Exact phrase match scores highest
        score = 10 if key in q else 0
        # Individual word matches
        score += sum(3 for w in key.split() if len(w) > 3 and w in q)
        if score > best_score:
            best_score, best_key = score, key

    if best_key and best_score > 0:
        entry = OFFLINE_KB[best_key]
        lang = "hi" if language == "hi" else "en"
        return {
            "simple_answer": entry.get(f"{lang}_simple", entry["en_simple"]),
            "detailed_answer": entry.get(f"{lang}_detailed"),
            "source_chapter": entry.get("chapter", ""),
            "provider": "offline_kb",
            "model": "keyword_match",
            "language": language,
        }
    return None


def _generic_offline_answer(question: str, context: str, language: str) -> Dict[str, Any]:
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', context) if s.strip()]
    if language == "hi":
        simple = " ".join(sentences[:3]) if sentences else f"'{question}' के बारे में अपनी पाठ्यपुस्तक देखें।"
        detailed = " ".join(sentences[:6]) if len(sentences) > 3 else "अपनी पाठ्यपुस्तक का उचित अध्याय देखें।"
    else:
        simple = " ".join(sentences[:3]) if sentences else f"Please refer to your textbook for: '{question}'."
        detailed = " ".join(sentences[:6]) if len(sentences) > 3 else "Please refer to the relevant chapter."
    return {"simple_answer": simple, "detailed_answer": detailed,
            "source_chapter": None, "provider": "offline_context",
            "model": "context_extraction", "language": language}


# ── Gemini API — pure urllib ──────────────────────────────────────────────
def _call_gemini_api(question: str, context: str, language: str,
                     api_key: str, model: str,
                     from_pdf: bool = False) -> Optional[Dict[str, Any]]:
    if not api_key:
        return None

    lang_note = "Respond ONLY in Hindi (Devanagari script)." if language == "hi" else "Respond in English."
    context_trimmed = context[:2000] if len(context) > 2000 else context

    if from_pdf and context_trimmed:
        prompt = (
            f"You are EduSarthi, a friendly AI tutor. {lang_note}\n\n"
            "Use ONLY the following textbook context to answer.\n\n"
            f"Context:\n{context_trimmed}\n\nQuestion: {question}\n\n"
            "1. Simple explanation (2-3 sentences)\n2. Detailed explanation (4-5 sentences)\n\n"
            'Reply ONLY with JSON: {"simple_answer": "...", "detailed_answer": "..."}'
        )
    elif not context_trimmed:
        not_found = ("यह प्रश्न आपकी पाठ्यपुस्तक में नहीं मिला, लेकिन सामान्य उत्तर:"
                     if language == "hi"
                     else "This topic wasn't found in your textbook, but here's a general answer:")
        prompt = (
            f"You are EduSarthi, a friendly AI tutor for Indian school students. {lang_note}\n\n"
            f"Question: {question}\n\n"
            f"Start simple_answer with: '{not_found}'\n"
            "Then give a helpful general educational answer.\n\n"
            'Reply ONLY with JSON: {"simple_answer": "...", "detailed_answer": "..."}'
        )
    else:
        prompt = (
            f"You are EduSarthi, a friendly AI tutor. {lang_note}\n\n"
            f"Context:\n{context_trimmed}\n\nQuestion: {question}\n\n"
            "1. Simple explanation (2-3 sentences)\n2. Detailed explanation (4-5 sentences)\n\n"
            'Reply ONLY with JSON: {"simple_answer": "...", "detailed_answer": "..."}'
        )

    gemini_model = model or "gemini-1.5-flash"
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{gemini_model}:generateContent?key={api_key}")
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 600},
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload,
                                 headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        raw = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        raw = re.sub(r"^```json\s*|^```\s*|```$", "", raw, flags=re.MULTILINE).strip()
        try:
            parsed = json.loads(raw)
            return {"simple_answer": parsed.get("simple_answer", ""),
                    "detailed_answer": parsed.get("detailed_answer"),
                    "source_chapter": None, "provider": "gemini",
                    "model": gemini_model, "language": language}
        except json.JSONDecodeError:
            return {"simple_answer": raw[:600],
                    "detailed_answer": raw[600:1200] if len(raw) > 600 else None,
                    "source_chapter": None, "provider": "gemini",
                    "model": gemini_model, "language": language}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        logger.warning(f"Gemini HTTP {e.code}: {body[:300]}")
        return None
    except Exception as e:
        logger.warning(f"Gemini failed: {e}")
        return None


# ── Claude API — pure urllib ──────────────────────────────────────────────
def _call_claude_api(question: str, context: str, language: str,
                     api_key: str) -> Optional[Dict[str, Any]]:
    if not api_key:
        return None
    lang = "Respond in Hindi (Devanagari script)." if language == "hi" else "Respond in English."
    ctx = context[:1500] if len(context) > 1500 else context
    payload = json.dumps({
        "model": "claude-haiku-4-5-20251001", "max_tokens": 600,
        "system": f"You are EduSarthi, a tutor for Indian school students. {lang} Reply ONLY with JSON: {{\"simple_answer\": \"...\", \"detailed_answer\": \"...\"}}",
        "messages": [{"role": "user", "content": f"Context:\n{ctx}\n\nQuestion: {question}"}],
    }).encode("utf-8")
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=payload,
        headers={"Content-Type": "application/json", "x-api-key": api_key, "anthropic-version": "2023-06-01"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        raw = re.sub(r"^```json\s*|^```\s*|```$", "", data["content"][0]["text"].strip(), flags=re.MULTILINE).strip()
        parsed = json.loads(raw)
        return {"simple_answer": parsed.get("simple_answer", ""), "detailed_answer": parsed.get("detailed_answer"),
                "source_chapter": None, "provider": "claude", "model": "claude-haiku-4-5-20251001", "language": language}
    except Exception as e:
        logger.warning(f"Claude failed: {e}")
        return None


# ── Main LLMGenerator ─────────────────────────────────────────────────────
class LLMGenerator:
    def __init__(self, provider: str = LLM_PROVIDER, api_key: str = LLM_API_KEY):
        import os
        self.provider = provider.lower()
        self.api_key = api_key
        self.model = LLM_MODEL
        self.claude_api_key = (os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY") or
                               (api_key if provider == "claude" else ""))
        logger.info(f"LLMGenerator: provider={self.provider}, key={'SET' if self.api_key else 'NOT SET'}")

    def generate_answer(self, question: str, context: str, language: str = "en",
                        simple: bool = True, detailed: bool = False,
                        from_pdf: bool = False) -> Dict[str, Any]:
        # 1. Gemini
        if self.provider == "gemini" and self.api_key:
            result = _call_gemini_api(question, context, language,
                                      self.api_key, self.model, from_pdf=from_pdf)
            if result:
                logger.info(f"Gemini ({'PDF' if from_pdf else 'general'}) ✓")
                return result
            logger.warning("Gemini failed — falling back")

        # 2. Claude
        if self.claude_api_key:
            result = _call_claude_api(question, context, language, self.claude_api_key)
            if result:
                logger.info("Claude ✓")
                return result

        # 3. Offline KB — covers 30+ school topics
        result = _find_offline_answer(question, language)
        if result:
            logger.info(f"Offline KB ✓ (matched topic)")
            return result

        # 4. Offline context extraction
        logger.info("Offline context extraction ✓")
        return _generic_offline_answer(question, context, language)

    def supports_language(self, language: str) -> bool:
        return language in ["en", "hi"]

    def get_info(self) -> Dict[str, Any]:
        return {
            "primary_provider": self.provider,
            "gemini_configured": self.provider == "gemini" and bool(self.api_key),
            "claude_configured": bool(self.claude_api_key),
            "model": self.model,
            "offline_kb_topics": list(OFFLINE_KB.keys()),
            "supported_languages": ["en", "hi"],
        }
