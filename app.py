from flask import Flask, render_template, request, jsonify
from transformers import pipeline
import random

app = Flask(__name__)

# === 1. Load AI pipelines ===
# These translation pipelines convert English ↔ Spanish.
# You can swap models or add more languages later.
translator_en_to_es = pipeline("translation_en_to_es", model="Helsinki-NLP/opus-mt-en-es")
translator_es_to_en = pipeline("translation_es_to_en", model="Helsinki-NLP/opus-mt-es-en")

# === 2. Bilingual facts data ===
# A list of dicts including English + Spanish versions of facts.
facts = [
    {
        "en": "Did you know? Hispanic Heritage Month runs from Sept 15 to Oct 15!",
        "es": "¿Sabías que? ¡El Mes de la Herencia Hispana se celebra del 15 de septiembre al 15 de octubre!"
    },
    {
        "en": "Latinos make up nearly 20% of the U.S. population today.",
        "es": "Los latinos constituyen casi el 20% de la población de los Estados Unidos hoy en día."
    },
    {
        "en": "Ellen Ochoa was the first Latina astronaut in space in 1993!",
        "es": "¡Ellen Ochoa fue la primera astronauta latina en el espacio en 1993!"
    },
    {
        "en": "Lin-Manuel Miranda, creator of Hamilton, is of Puerto Rican heritage.",
        "es": "Lin-Manuel Miranda, creador de Hamilton, es de ascendencia puertorriqueña."
    },
    {
        "en": "César Chávez fought for the rights of farm workers and co-founded the United Farm Workers union.",
        "es": "César Chávez luchó por los derechos de los trabajadores agrícolas y cofundó el sindicato United Farm Workers."
    },
    {
        "en": "Sonia Sotomayor became the first Latina Supreme Court Justice in U.S. history.",
        "es": "Sonia Sotomayor se convirtió en la primera jueza latina de la Corte Suprema en la historia de EE.UU."
    },
    {
        "en": "Spanish is the second most spoken language in the world by native speakers!",
        "es": "¡El español es el segundo idioma más hablado del mundo por hablantes nativos!"
    },
    {
        "en": "Celia Cruz, known as the 'Queen of Salsa,' brought Afro-Cuban rhythms to global audiences.",
        "es": "Celia Cruz, conocida como la 'Reina de la Salsa', llevó los ritmos afrocubanos al público mundial."
    },
    {
        "en": "Frida Kahlo, one of Mexico’s most famous artists, is celebrated for her self-portraits and expression of identity.",
        "es": "Frida Kahlo, una de las artistas más famosas de México, es celebrada por sus autorretratos y su expresión de identidad."
    },
    {
        "en": "Mexico introduced chocolate, chili peppers, and corn to the world!",
        "es": "¡México introdujo el chocolate, los chiles y el maíz al mundo!"
    },
    {
        "en": "The first Hispanic astronaut was Franklin Chang-Díaz, who flew on seven space missions.",
        "es": "El primer astronauta hispano fue Franklin Chang-Díaz, quien voló en siete misiones espaciales."
    },
    {
        "en": "Jennifer Lopez became one of the first Latina entertainers to achieve worldwide fame in both music and film.",
        "es": "Jennifer Lopez se convirtió en una de las primeras artistas latinas en lograr fama mundial en la música y el cine."
    },
    {
        "en": "Hispanic-owned businesses are the fastest-growing segment of small businesses in the U.S.",
        "es": "Las empresas propiedad de hispanos son el sector de negocios de más rápido crecimiento en Estados Unidos."
    },
    {
        "en": "Puerto Rico has a rich culture blending Taíno, African, and Spanish influences.",
        "es": "Puerto Rico tiene una rica cultura que mezcla influencias taínas, africanas y españolas."
    },
    {
        "en": "In 2009, Sonia Sotomayor became the first Hispanic Supreme Court Justice.",
        "es": "En 2009, Sonia Sotomayor se convirtió en la primera jueza hispana de la Corte Suprema."
    },
    {
        "en": "Hispanic Heritage Month begins on Sept 15 to honor the independence days of five Latin American countries.",
        "es": "El Mes de la Herencia Hispana comienza el 15 de septiembre para honrar las independencias de cinco países latinoamericanos."
    },
    {
        "en": "Latino music genres like reggaetón, bachata, and salsa have influenced global pop culture.",
        "es": "Los géneros musicales latinos como el reggaetón, la bachata y la salsa han influido en la cultura pop mundial."
    },
    {
        "en": "The first Hispanic woman in the U.S. Congress was Ileana Ros-Lehtinen, elected in 1989.",
        "es": "La primera mujer hispana en el Congreso de EE.UU. fue Ileana Ros-Lehtinen, elegida en 1989."
    },
    {
        "en": "Latinos have contributed to science, politics, sports, and the arts across generations.",
        "es": "Los latinos han contribuido a la ciencia, la política, el deporte y las artes a lo largo de las generaciones."
    },
    {
        "en": "Over 60 million people of Hispanic heritage live in the United States today!",
        "es": "¡Más de 60 millones de personas de herencia hispana viven hoy en los Estados Unidos!"
    },
    # --- STEM-focused facts ---
    {
        "en": "Dr. Antonia Novello became the first Hispanic woman to serve as U.S. Surgeon General in 1990.",
        "es": "La Dra. Antonia Novello se convirtió en la primera mujer hispana en servir como Cirujana General de EE.UU. en 1990."
    },
    {
        "en": "Mario Molina, a Mexican chemist, won the Nobel Prize in Chemistry for his research on the ozone layer.",
        "es": "Mario Molina, un químico mexicano, ganó el Premio Nobel de Química por su investigación sobre la capa de ozono."
    },
    {
        "en": "Ellen Ochoa not only went to space but also became the first Hispanic director of NASA’s Johnson Space Center.",
        "es": "Ellen Ochoa no solo fue al espacio, sino que también se convirtió en la primera directora hispana del Centro Espacial Johnson de la NASA."
    },
    {
        "en": "Luis von Ahn, a Guatemalan computer scientist, created CAPTCHA and co-founded Duolingo.",
        "es": "Luis von Ahn, un científico informático guatemalteco, creó el CAPTCHA y cofundó Duolingo."
    },
    {
        "en": "Dr. France Córdova, an astrophysicist of Mexican-American descent, served as Director of the National Science Foundation.",
        "es": "La Dra. France Córdova, una astrofísica de ascendencia mexicana, fue Directora de la Fundación Nacional de Ciencia (NSF)."
    }
]

# ----------------------------
# === 3. Routes ===
@app.route("/")
def index():
    """ Serve the HTML interface"""
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    """Receive user message and return translation or fact."""
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "")
    lang = data.get("lang", "en")
    # Default response
    response = ""

    if user_message.lower() == "fact":
        # Return a random fact in the selected language
        fact = random.choice(facts)
        response = fact["es"] if lang == "es" else fact["en"]
    else:
        # Translate user messages
        if lang == "en":
            # Translate English → Spanish
            # result is usually a list of dicts
            response = translator_en_to_es(user_message)[0]["translation_text"]  # type: ignore
        elif lang == "es":
            # Translate Spanish → English
            response = translator_es_to_en(user_message)[0]["translation_text"]  # type: ignore
        else:
            response = "Sorry, I only support English <-> Spanish."

    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)

