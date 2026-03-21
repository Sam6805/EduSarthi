"""LLM-based answer generation service."""

import json
import re
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

from app.utils.helpers import setup_logger
from app.config import LLM_PROVIDER, LLM_API_KEY, LLM_MODEL, LLM_TEMPERATURE

logger = setup_logger(__name__)

OFFLINE_KB: Dict[str, Dict[str, str]] = {
    "matter": {"en_simple": "Matter is anything that has mass and occupies space. It exists in three states: solid, liquid, and gas.", "en_detailed": "Matter is made of atoms and molecules. Solids have fixed shape; liquids flow; gases expand. Heating causes state changes (ice→water→steam).", "hi_simple": "पदार्थ वह है जिसका द्रव्यमान हो और जो स्थान घेरे। यह ठोस, द्रव और गैस में पाया जाता है।", "hi_detailed": "पदार्थ परमाणुओं से बना है। गर्म करने पर अवस्था बदलती है।", "chapter": "Chapter 1: Matter in Our Surroundings"},
    "diffusion": {"en_simple": "Diffusion is the spreading of particles from high concentration to low concentration. Example: perfume smell spreading across a room.", "en_detailed": "Particles move from high to low concentration until evenly spread. Fastest in gases, slowest in solids. Higher temperature = faster diffusion.", "hi_simple": "विसरण में कण अधिक सांद्रता से कम सांद्रता की ओर फैलते हैं। उदाहरण: इत्र की खुशबू का फैलना।", "hi_detailed": "गैसों में सबसे तेज, ठोस में सबसे धीमा। तापमान बढ़ने से दर बढ़ती है।", "chapter": "Chapter 1: Matter in Our Surroundings"},
    "evaporation": {"en_simple": "Evaporation is when a liquid turns to gas below its boiling point. Example: wet clothes drying in sunlight.", "en_detailed": "Happens at liquid surface. Increases with temperature, surface area, and wind. Causes cooling — sweating cools your body.", "hi_simple": "वाष्पीकरण में द्रव क्वथनांक से नीचे गैस में बदलता है। उदाहरण: गीले कपड़ों का सूखना।", "hi_detailed": "द्रव की सतह पर होता है। ठंडक उत्पन्न करता है।", "chapter": "Chapter 1: Matter in Our Surroundings"},
    "solution": {"en_simple": "A solution is a homogeneous mixture where solute dissolves in solvent. Example: salt in water.", "en_detailed": "Saturated solution cannot dissolve more solute. Solubility of solids increases with temperature; gases decrease.", "hi_simple": "विलयन में विलेय, विलायक में घुलता है। उदाहरण: पानी में नमक।", "hi_detailed": "संतृप्त विलयन में और विलेय नहीं घुल सकता।", "chapter": "Chapter 2: Is Matter Around Us Pure?"},
    "atom": {"en_simple": "An atom is the smallest particle of an element, with a nucleus (protons+neutrons) and electrons in shells.", "en_detailed": "Atomic number = protons. Mass number = protons+neutrons. Isotopes: same protons, different neutrons.", "hi_simple": "परमाणु तत्व का सबसे छोटा कण है। केंद्रक में प्रोटॉन+न्यूट्रॉन, चारों ओर इलेक्ट्रॉन।", "hi_detailed": "परमाणु क्रमांक = प्रोटॉन। द्रव्यमान संख्या = प्रोटॉन+न्यूट्रॉन।", "chapter": "Chapter 4: Atoms and Molecules"},
    "molecule": {"en_simple": "A molecule is the smallest independent particle of a substance, made of two or more atoms bonded together.", "en_detailed": "Homoatomic (O₂, H₂) or heteroatomic (H₂O, CO₂). Molecular mass = sum of atomic masses.", "hi_simple": "अणु पदार्थ का सबसे छोटा स्वतंत्र कण है।", "hi_detailed": "समपरमाणुक (O₂) या विषमपरमाणुक (H₂O)।", "chapter": "Chapter 4: Atoms and Molecules"},
    "cell": {"en_simple": "A cell is the basic unit of life with a membrane, cytoplasm, and nucleus.", "en_detailed": "Animal cells: membrane, nucleus, mitochondria. Plant cells add: cell wall, chloroplasts, vacuole.", "hi_simple": "कोशिका जीवन की मूल इकाई है।", "hi_detailed": "पादप कोशिका में कोशिका भित्ति, हरित लवक, रिक्तिका अतिरिक्त होते हैं।", "chapter": "Chapter 5: The Fundamental Unit of Life"},
    "photosynthesis": {"en_simple": "Plants make food using sunlight, water, and CO₂, releasing oxygen.", "en_detailed": "Occurs in chloroplasts. Equation: 6CO₂+6H₂O+light → C₆H₁₂O₆+6O₂.", "hi_simple": "पौधे सूर्य प्रकाश, पानी और CO₂ से भोजन बनाते हैं।", "hi_detailed": "क्लोरोप्लास्ट में होता है। 6CO₂+6H₂O+प्रकाश → C₆H₁₂O₆+6O₂।", "chapter": "Chapter 6: Life Processes"},
    "respiration": {"en_simple": "Cells break down glucose to release energy. Aerobic respiration uses oxygen and produces CO₂+water.", "en_detailed": "Aerobic: C₆H₁₂O₆+6O₂ → 6CO₂+6H₂O+ATP. Anaerobic: lactic acid (muscles) or ethanol+CO₂ (yeast).", "hi_simple": "कोशिकाएँ ग्लूकोज तोड़कर ऊर्जा (ATP) बनाती हैं।", "hi_detailed": "वायवीय: C₆H₁₂O₆+6O₂ → CO₂+H₂O+ऊर्जा। अवायवीय: लैक्टिक एसिड।", "chapter": "Chapter 6: Life Processes"},
    "osmosis": {"en_simple": "Osmosis is water moving through a semi-permeable membrane from high to low water concentration.", "en_detailed": "Hypotonic solution → water enters cell → swells. Hypertonic → water leaves → shrinks (plasmolysis).", "hi_simple": "परासरण में जल अर्ध-पारगम्य झिल्ली से अधिक से कम जल सांद्रता की ओर जाता है।", "hi_detailed": "हाइपोटोनिक में कोशिका फूलती है, हाइपरटोनिक में सिकुड़ती है।", "chapter": "Chapter 6: Life Processes"},
    "tissue": {"en_simple": "Tissue is a group of similar cells performing a specific function. Example: muscle tissue for movement.", "en_detailed": "Plant: meristematic, permanent. Animal: epithelial, connective, muscular, nervous.", "hi_simple": "ऊतक समान कोशिकाओं का समूह है।", "hi_detailed": "पादप: विभज्योतक, स्थायी। जंतु: उपकला, संयोजी, पेशीय, तंत्रिका।", "chapter": "Chapter 6: Tissues"},
    "force": {"en_simple": "Force is a push or pull measured in Newtons. It can move, stop, or change direction of objects.", "en_detailed": "Newton's laws: (1) inertia, (2) F=ma, (3) action-reaction.", "hi_simple": "बल धक्का या खिंचाव है। इकाई न्यूटन।", "hi_detailed": "न्यूटन के नियम: जड़त्व, F=ma, क्रिया-प्रतिक्रिया।", "chapter": "Chapter 9: Force and Laws of Motion"},
    "friction": {"en_simple": "Friction opposes relative motion between surfaces. Rough surfaces have more friction.", "en_detailed": "Types: static, kinetic, rolling (smallest), fluid. F=μN. Lubricants reduce friction.", "hi_simple": "घर्षण गति का विरोध करता है।", "hi_detailed": "प्रकार: स्थैतिक, गतिज, लोटनिक (न्यूनतम), तरल। F=μN।", "chapter": "Chapter 12: Friction"},
    "gravity": {"en_simple": "Gravity attracts objects. Weight = mass × g (≈9.8 m/s²).", "en_detailed": "F=Gm₁m₂/r². Keeps planets in orbit. Free fall: same acceleration for all objects.", "hi_simple": "गुरुत्वाकर्षण वस्तुओं को खींचता है। भार = द्रव्यमान × g।", "hi_detailed": "F=Gm₁m₂/r²। ग्रहों को कक्षा में रखता है।", "chapter": "Chapter 10: Gravitation"},
    "pressure": {"en_simple": "Pressure = Force/Area. Smaller area = more pressure. Unit: Pascal.", "en_detailed": "Fluid pressure: P=ρgh. Pascal's law: transmits equally (hydraulic systems). Atmospheric ≈101,325 Pa.", "hi_simple": "दाब = बल ÷ क्षेत्रफल। इकाई पास्कल।", "hi_detailed": "द्रव में P=ρgh। पास्कल का नियम: हाइड्रोलिक ब्रेक।", "chapter": "Chapter 11: Force and Pressure"},
    "sound": {"en_simple": "Sound is energy from vibrations, travelling as longitudinal waves. Cannot travel in vacuum. Speed in air ≈343 m/s.", "en_detailed": "Frequency (Hz) = pitch. Amplitude = loudness. Hearing: 20–20,000 Hz. Ultrasound >20,000 Hz.", "hi_simple": "ध्वनि कंपन से उत्पन्न ऊर्जा है। निर्वात में नहीं चलती।", "hi_detailed": "आवृत्ति = तारत्व। मानव श्रव्यता: 20–20,000 Hz।", "chapter": "Chapter 12: Sound"},
    "light": {"en_simple": "Light travels at 3×10⁸ m/s, reflects and refracts. White light splits into VIBGYOR through a prism.", "en_detailed": "Reflection: angle in = angle out. Refraction: Snell's law. Total internal reflection → optical fibre.", "hi_simple": "प्रकाश 3×10⁸ m/s से चलता है।", "hi_detailed": "परावर्तन, अपवर्तन, पूर्ण आंतरिक परावर्तन।", "chapter": "Chapter 16: Light"},
    "electricity": {"en_simple": "Electricity is electron flow. Current in Amperes, Voltage in Volts, Resistance in Ohms.", "en_detailed": "Ohm's law: V=IR. Series: currents equal. Parallel: voltages equal.", "hi_simple": "विद्युत इलेक्ट्रॉन प्रवाह है।", "hi_detailed": "ओम का नियम: V=IR।", "chapter": "Chapter 12: Electricity"},
    "magnetism": {"en_simple": "Magnets attract iron. North and South poles — like poles repel, unlike attract.", "en_detailed": "Field lines N→S. Electromagnet: temporary, from current. Earth is a giant magnet.", "hi_simple": "चुम्बक लोहे को खींचता है। उत्तर-दक्षिण ध्रुव।", "hi_detailed": "विद्युत चुम्बक अस्थायी। पृथ्वी एक विशाल चुम्बक है।", "chapter": "Chapter 13: Magnetic Effects of Electric Current"},
    "acid": {"en_simple": "Acids taste sour, turn blue litmus red, release H⁺ ions. Examples: HCl, H₂SO₄, citric acid.", "en_detailed": "Strong acids fully ionise. pH<7. Acid+metal→H₂. Acid+base→salt+water.", "hi_simple": "अम्ल खट्टे होते हैं, नीले लिटमस को लाल करते हैं।", "hi_detailed": "pH<7। अम्ल+धातु→H₂। अम्ल+क्षार→लवण+जल।", "chapter": "Chapter 2: Acids, Bases and Salts"},
    "base": {"en_simple": "Bases taste bitter, feel soapy, turn red litmus blue, release OH⁻ ions.", "en_detailed": "Strong bases (NaOH) fully dissociate. pH>7. Base+acid→salt+water.", "hi_simple": "क्षार कड़वे, चिकने होते हैं। लाल लिटमस को नीला करते हैं।", "hi_detailed": "pH>7। क्षार+अम्ल→लवण+जल।", "chapter": "Chapter 2: Acids, Bases and Salts"},
    "chemical reaction": {"en_simple": "Chemical reactions transform reactants into products. Signs: colour change, gas, heat, precipitate.", "en_detailed": "Types: combination, decomposition, displacement, combustion. Mass conservation law.", "hi_simple": "रासायनिक अभिक्रिया में अभिकारक नए पदार्थ में बदलते हैं।", "hi_detailed": "प्रकार: संयोजन, अपघटन, विस्थापन, दहन।", "chapter": "Chapter 1: Chemical Reactions and Equations"},
    "algebra": {"en_simple": "Algebra uses letters for unknowns. Solve x+5=12 by subtracting 5: x=7.", "en_detailed": "Steps: simplify → variables one side → constants other → divide by coefficient.", "hi_simple": "बीजगणित में अज्ञात को अक्षर से दर्शाते हैं।", "hi_detailed": "हल: सरल → चर एक तरफ → अचर दूसरी तरफ → भाग दें।", "chapter": "Chapter 4: Simple Equations"},
    "triangle": {"en_simple": "Triangle: 3 sides, 3 angles summing to 180°. Pythagoras: a²+b²=c².", "en_detailed": "Types: equilateral, isosceles, scalene. Area=½×base×height.", "hi_simple": "त्रिभुज: 3 भुजाएँ, कोण योग=180°।", "hi_detailed": "प्रकार: समबाहु, समद्विबाहु, विषमबाहु। क्षेत्रफल=½×आधार×ऊँचाई।", "chapter": "Chapter 6: Triangles"},
    "fraction": {"en_simple": "Fraction = part/whole. To add different denominators, find LCM first. ½+⅓=5/6.", "en_detailed": "Types: proper, improper, mixed. Multiply: num×num, den×den. Divide: multiply by reciprocal.", "hi_simple": "भिन्न पूर्ण का भाग है।", "hi_detailed": "गुणा: अंश×अंश, हर×हर। भाग: व्युत्क्रम से गुणा।", "chapter": "Chapter 2: Fractions and Decimals"},
    "ecosystem": {"en_simple": "An ecosystem is living organisms interacting with their non-living environment. Example: forest, pond.", "en_detailed": "Biotic: producers, consumers, decomposers. Abiotic: sunlight, water, temperature. Energy flows via food chains.", "hi_simple": "पारितंत्र में जीवित और अजीवित घटक परस्पर क्रिया करते हैं।", "hi_detailed": "जैविक: उत्पादक, उपभोक्ता, अपघटक। अजैविक: सूर्य प्रकाश, जल।", "chapter": "Chapter 15: Our Environment"},
    "food chain": {"en_simple": "Food chain shows who eats whom. Starts with producers (plants). Example: grass→grasshopper→frog→snake→eagle.", "en_detailed": "Only ~10% energy passes to next level. Decomposers break down dead matter.", "hi_simple": "खाद्य श्रृंखला: कौन किसे खाता है। उत्पादक से शुरू।", "hi_detailed": "हर स्तर पर ~10% ऊर्जा आगे जाती है।", "chapter": "Chapter 15: Our Environment"},
}


def _find_offline_answer(question: str, language: str) -> Optional[Dict[str, Any]]:
    q = question.lower()
    best_key, best_score = None, 0
    for key in OFFLINE_KB:
        score = 10 if key in q else 0
        score += sum(3 for w in key.split() if len(w) > 3 and w in q)
        if score > best_score:
            best_score, best_key = score, key
    if best_key and best_score > 0:
        entry = OFFLINE_KB[best_key]
        lang = "hi" if language == "hi" else "en"
        return {"simple_answer": entry.get(f"{lang}_simple", entry["en_simple"]),
                "detailed_answer": entry.get(f"{lang}_detailed"),
                "source_chapter": entry.get("chapter", ""),
                "provider": "offline_kb", "model": "keyword_match", "language": language}
    return None


def _generic_offline_answer(question: str, context: str, language: str) -> Dict[str, Any]:
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', context) if s.strip()]
    if language == "hi":
        simple = " ".join(sentences[:3]) if sentences else f"'{question}' के बारे में अपनी पाठ्यपुस्तक देखें।"
        detailed = " ".join(sentences[:6]) if len(sentences) > 3 else "अपनी पाठ्यपुस्तक देखें।"
    else:
        simple = " ".join(sentences[:3]) if sentences else f"Please refer to your textbook for: '{question}'."
        detailed = " ".join(sentences[:6]) if len(sentences) > 3 else "Please refer to the relevant chapter."
    return {"simple_answer": simple, "detailed_answer": detailed,
            "source_chapter": None, "provider": "offline_context", "model": "context_extraction", "language": language}


def _call_gemini_api(question: str, context: str, language: str,
                     api_key: str, model: str, from_pdf: bool = False) -> Optional[Dict[str, Any]]:
    if not api_key:
        return None

    lang_note = "Respond ONLY in Hindi (Devanagari script)." if language == "hi" else "Respond in English."
    context_trimmed = context[:2000] if len(context) > 2000 else context

    if from_pdf and context_trimmed:
        # Uploaded PDF — answer strictly from context
        prompt = (
            f"You are EduSarthi, a friendly AI tutor. {lang_note}\n\n"
            "Use ONLY the following textbook context to answer.\n\n"
            f"Context:\n{context_trimmed}\n\nQuestion: {question}\n\n"
            "1. Simple explanation (2-3 sentences)\n2. Detailed explanation (4-5 sentences)\n\n"
            'Reply ONLY with JSON: {"simple_answer": "...", "detailed_answer": "..."}'
        )
    elif context_trimmed:
        # Sample textbook — curriculum info as context, give class-appropriate answer
        prompt = (
            f"You are EduSarthi, a friendly AI tutor for Indian school students. {lang_note}\n\n"
            f"{context_trimmed}\n\n"
            f"Student question: {question}\n\n"
            "Give a curriculum-aligned answer appropriate for the class level above.\n"
            "1. Simple explanation (2-3 easy sentences)\n"
            "2. Detailed explanation (4-5 sentences with examples)\n\n"
            'Reply ONLY with JSON: {"simple_answer": "...", "detailed_answer": "..."}'
        )
    else:
        # No context — general answer with note
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

    gemini_model = model or "gemini-1.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent?key={api_key}"
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


def _call_claude_api(question: str, context: str, language: str, api_key: str) -> Optional[Dict[str, Any]]:
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
                logger.info(f"Gemini ({'PDF' if from_pdf else 'curriculum/general'}) ✓")
                return result
            logger.warning("Gemini failed — falling back")

        # 2. Claude
        if self.claude_api_key:
            result = _call_claude_api(question, context, language, self.claude_api_key)
            if result:
                logger.info("Claude ✓")
                return result

        # 3. Offline KB
        result = _find_offline_answer(question, language)
        if result:
            logger.info("Offline KB ✓")
            return result

        # 4. Context extraction
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
