import os
import secrets
from datetime import date
from pathlib import Path

from flask import (
    Flask, abort, flash, jsonify, redirect, render_template,
    request, session, url_for
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, UniqueConstraint, inspect, or_, text
from sqlalchemy.exc import IntegrityError

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "cineflix.db"
db = SQLAlchemy()


class Reservacion(db.Model):
    __tablename__ = "reservaciones"
    __table_args__ = (
        CheckConstraint("boletos BETWEEN 1 AND 10", name="ck_reservaciones_boletos"),
    )

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    correo = db.Column(db.String(120), nullable=False)
    pelicula = db.Column(db.String(255), nullable=False)
    fecha = db.Column(db.String(10), nullable=False)
    horario = db.Column(db.String(5), nullable=False)
    boletos = db.Column(db.Integer, nullable=False)
    sala = db.Column(db.String(20), nullable=False)
    folio = db.Column(db.String(12), nullable=False, unique=True)
    asientos = db.relationship(
        "AsientoReservado",
        cascade="all, delete-orphan",
        backref="reservacion",
        order_by="AsientoReservado.asiento",
    )
    creado_en = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(),
    )


class AsientoReservado(db.Model):
    __tablename__ = "asientos_reservados"
    __table_args__ = (
        UniqueConstraint(
            "pelicula", "fecha", "horario", "sala", "asiento",
            name="uq_asiento_por_funcion",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    reservacion_id = db.Column(
        db.Integer,
        db.ForeignKey("reservaciones.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    pelicula = db.Column(db.String(255), nullable=False)
    fecha = db.Column(db.String(10), nullable=False)
    horario = db.Column(db.String(5), nullable=False)
    sala = db.Column(db.String(20), nullable=False)
    asiento = db.Column(db.String(3), nullable=False)


PELICULAS_CARTELERA = [
    {
        "titulo": "Ebenezer: Los fantasmas de Navidad",
        "poster": "https://mx.web.img2.acsta.net/c_310_420/img/a3/f2/a3f2a6db1a9161e58d7e390450e4e8a5.jpg",
    },
    {
        "titulo": "Yo soy Rocky",
        "poster": "https://mx.web.img3.acsta.net/c_310_420/img/85/43/854327c756bc3c5fc7659e776a55eeb7.jpg",
    },
    {
        "titulo": "Atrápelo quien pueda",
        "poster": "https://mx.web.img3.acsta.net/c_310_420/img/a9/3d/a93d7343d003bff07573d70d3a950b56.jpg",
    },
    {
        "titulo": "Petardos & Magnolias",
        "poster": "https://mx.web.img3.acsta.net/c_310_420/img/76/14/76143003263b40692e5b4c65fce13706.jpg",
    },
    {
        "titulo": "Ramayana: El nacimiento de una leyenda",
        "poster": "https://mx.web.img2.acsta.net/c_310_420/img/6a/f4/6af4905181b7dc639c95e6c2e5225688.jpg",
    },
    {
        "titulo": "Cómo robar un banco",
        "poster": "https://mx.web.img3.acsta.net/c_310_420/img/7e/cc/7eccd19f0ee4871afe8086537f2860aa.jpg",
    },
    {
        "titulo": "Fiesta Pagäna",
        "poster": "https://mx.web.img2.acsta.net/c_310_420/img/60/6c/606c1fee3a4f3156071d48c1f4b9c770.jpg",
    },
    {
        "titulo": "Mi robot y yo",
        "poster": "https://mx.web.img3.acsta.net/c_310_420/img/cc/83/cc8380d5c8127cdabff607a3ba7abb4e.jpg",
    },
    {
        "titulo": "El caso de los milagros",
        "poster": "https://mx.web.img3.acsta.net/c_310_420/img/f2/b3/f2b39570ddcf453936c07672cc1e99dc.jpg",
    },
    {
        "titulo": "Stray Kids World Tour: RUN IT",
        "poster": "https://mx.web.img3.acsta.net/c_310_420/img/e0/6c/e06cee9ab975062857e2028a783617c7.jpg",
    },
    {
        "titulo": "EXO PLANET #6: EXhOrizon",
        "poster": "https://mx.web.img2.acsta.net/c_310_420/img/ce/3e/ce3e4850f0b3fbf90e620a5a05763933.jpg",
    },
    {
        "titulo": "Romeo y Julieta: Ópera de París",
        "poster": "https://mx.web.img2.acsta.net/c_310_420/img/fa/f7/faf7ee4b4d1cce8938b987facb797913.jpg",
    },
    {
        "titulo": "Hoshimachi Suisei: Once Upon a Stellar",
        "poster": "https://mx.web.img3.acsta.net/c_310_420/img/cb/b2/cbb22241ec403529888ffc1ea1dd88db.jpg",
    },
    {
        "titulo": "Rápidos y furiosos",
        "poster": "https://upload.wikimedia.org/wikipedia/en/5/54/Fast_and_the_furious_poster.jpg",
    },
    {
        "titulo": "Interestelar",
        "poster": "https://upload.wikimedia.org/wikipedia/en/b/bc/Interstellar_film_poster.jpg",
    },
    {
        "titulo": "La Purga: La noche de la expiación",
        "poster": "https://upload.wikimedia.org/wikipedia/en/9/94/The_Purge_film_poster.jpg",
    },
]
PELICULAS = [pelicula["titulo"] for pelicula in PELICULAS_CARTELERA]
HORARIOS = ["14:00", "17:00", "20:00"]
SALAS = ["Tradicional", "VIP", "3D"]
FILAS_ASIENTOS = ["A", "B", "C", "D", "E"]
ASIENTOS_POR_FILA = 8
ASIENTOS_DISPONIBLES = {
    f"{fila}{numero}"
    for fila in FILAS_ASIENTOS
    for numero in range(1, ASIENTOS_POR_FILA + 1)
}
INFO_PELICULAS = {
    "Ebenezer: Los fantasmas de Navidad": ("Fantasía", "Una historia navideña de fantasmas y segundas oportunidades."),
    "Yo soy Rocky": ("Drama", "El origen de una historia de perseverancia que convirtió a un boxeador en leyenda."),
    "Atrápelo quien pueda": ("Comedia romántica", "Un padre vuelve a las citas y descubre que el amor puede estar más cerca de lo esperado."),
    "Petardos & Magnolias": ("Drama romántico", "Un romance juvenil se enfrenta a secretos y decisiones que amenazan su futuro."),
    "Ramayana: El nacimiento de una leyenda": ("Aventura", "Un príncipe emprende un viaje épico para rescatar a su esposa."),
    "Cómo robar un banco": ("Suspenso", "Un grupo de ladrones planea un asalto mientras atrae la atención del FBI."),
    "Fiesta Pagäna": ("Música", "La trayectoria de Mägo de Oz y su ascenso en la escena musical."),
    "Mi robot y yo": ("Animación", "Una joven astronauta y su robot guardián exploran el vínculo que los une."),
    "El caso de los milagros": ("Documental", "Un periodista investiga historias extraordinarias y la posibilidad de los milagros."),
    "Stray Kids World Tour: RUN IT": ("Concierto", "Una presentación en vivo de Stray Kids desde el Tokyo Dome."),
    "EXO PLANET #6: EXhOrizon": ("Concierto", "El cierre de la sexta gira de EXO llega a la pantalla grande."),
    "Romeo y Julieta: Ópera de París": ("Ópera", "La historia de dos jóvenes enamorados separados por la rivalidad de sus familias."),
    "Hoshimachi Suisei: Once Upon a Stellar": ("Concierto", "El concierto final de la gira 2026 de Hoshimachi Suisei."),
    "Rápidos y furiosos": ("Acción", "Un policía encubierto se infiltra en el mundo de las carreras callejeras."),
    "Interestelar": ("Ciencia ficción", "Una misión espacial atraviesa un agujero de gusano en busca de un futuro para la humanidad."),
    "La Purga: La noche de la expiación": ("Terror", "Una familia intenta sobrevivir una noche en la que el crimen queda sin castigo."),
}


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    database_url = os.environ.get("DATABASE_URL")
    if database_url and database_url.startswith("postgres://"):
        database_url = "postgresql+psycopg://" + database_url[len("postgres://"):]
    elif database_url and database_url.startswith("postgresql://"):
        database_url = "postgresql+psycopg://" + database_url[len("postgresql://"):]

    if os.environ.get("RENDER") and not database_url:
        raise RuntimeError("Configura DATABASE_URL para conectar la base de Neon.")

    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key and os.environ.get("RENDER"):
        raise RuntimeError("Configura SECRET_KEY en el entorno de Render.")

    app.config.from_mapping(
        SECRET_KEY=secret_key or "dev-cineflix-cambia-esta-clave",
        SQLALCHEMY_DATABASE_URI=database_url or f"sqlite:///{DATABASE.as_posix()}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={"pool_pre_ping": True},
        MAX_CONTENT_LENGTH=2 * 1024 * 1024,
    )

    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    db.init_app(app)

    def csrf_token():
        if "_csrf_token" not in session:
            session["_csrf_token"] = secrets.token_urlsafe(32)
        return session["_csrf_token"]

    app.jinja_env.globals["csrf_token"] = csrf_token

    @app.before_request
    def protect_post_requests():
        if request.method == "POST":
            sent_token = request.form.get("_csrf_token", "")
            saved_token = session.get("_csrf_token", "")
            if not sent_token or not saved_token or not secrets.compare_digest(sent_token, saved_token):
                abort(400, description="La sesión del formulario expiró. Recarga la página e inténtalo de nuevo.")

    def cartelera_para_vista():
        return [
            {
                **pelicula,
                "genero": INFO_PELICULAS[pelicula["titulo"]][0],
                "sinopsis": INFO_PELICULAS[pelicula["titulo"]][1],
            }
            for pelicula in PELICULAS_CARTELERA
        ]

    def contexto_reserva(errores, form_data, asientos_seleccionados):
        return {
            "errores": errores,
            "form_data": form_data,
            "peliculas": PELICULAS,
            "horarios": HORARIOS,
            "salas": SALAS,
            "cartelera": cartelera_para_vista(),
            "hoy": date.today().isoformat(),
            "filas_asientos": FILAS_ASIENTOS,
            "asientos_por_fila": range(1, ASIENTOS_POR_FILA + 1),
            "asientos_seleccionados": asientos_seleccionados,
            "asientos_api_url": url_for("asientos_funcion"),
        }

    @app.route("/", methods=["GET", "POST"])
    def reserva():
        errores = []
        form_data = {}
        asientos_seleccionados = []

        if request.method == "POST":
            form_data = request.form.to_dict()
            asientos_seleccionados = request.form.getlist("asientos")
            nombre = form_data.get("nombre", "").strip()
            correo = form_data.get("correo", "").strip()
            pelicula = form_data.get("pelicula", "")
            fecha = form_data.get("fecha", "")
            horario = form_data.get("horario", "")
            boletos_txt = form_data.get("boletos", "")
            sala = form_data.get("sala", "")

            if not nombre or len(nombre) > 80:
                errores.append("Escribe un nombre de máximo 80 caracteres.")
            if not correo or len(correo) > 120 or "@" not in correo or "." not in correo.split("@")[-1]:
                errores.append("Escribe un correo electrónico válido.")
            if pelicula not in PELICULAS:
                errores.append("Selecciona una película válida.")
            try:
                fecha_obj = date.fromisoformat(fecha)
                if fecha_obj < date.today():
                    errores.append("La fecha no puede ser anterior a hoy.")
            except ValueError:
                errores.append("Selecciona una fecha válida.")
            if horario not in HORARIOS:
                errores.append("Selecciona un horario válido.")
            try:
                boletos = int(boletos_txt)
                if not 1 <= boletos <= 10:
                    errores.append("La cantidad debe estar entre 1 y 10 boletos.")
            except (ValueError, TypeError):
                boletos = 0
                errores.append("La cantidad de boletos debe ser un número.")
            if sala not in SALAS:
                errores.append("Selecciona un tipo de sala válido.")
            if len(asientos_seleccionados) != len(set(asientos_seleccionados)):
                errores.append("No repitas asientos.")
            if any(asiento not in ASIENTOS_DISPONIBLES for asiento in asientos_seleccionados):
                errores.append("Selecciona asientos válidos.")
            if len(asientos_seleccionados) != boletos:
                errores.append("Selecciona exactamente un asiento por boleto.")

            if errores:
                return render_template(
                    "reserva.html",
                    **contexto_reserva(errores, form_data, asientos_seleccionados),
                ), 400

            datos_funcion = (
                AsientoReservado.pelicula == pelicula,
                AsientoReservado.fecha == fecha,
                AsientoReservado.horario == horario,
                AsientoReservado.sala == sala,
            )
            ocupados = set(db.session.execute(
                db.select(AsientoReservado.asiento).where(
                    *datos_funcion,
                    AsientoReservado.asiento.in_(asientos_seleccionados),
                )
            ).scalars())
            if ocupados:
                errores.append(
                    f"Los asientos {', '.join(sorted(ocupados))} ya se reservaron. Elige otros."
                )
                return render_template(
                    "reserva.html",
                    **contexto_reserva(errores, form_data, asientos_seleccionados),
                ), 409

            reservacion = Reservacion(
                nombre=nombre,
                correo=correo,
                pelicula=pelicula,
                fecha=fecha,
                horario=horario,
                boletos=boletos,
                sala=sala,
                folio=secrets.token_hex(6).upper(),
            )
            reservacion.asientos = [
                AsientoReservado(
                    pelicula=pelicula,
                    fecha=fecha,
                    horario=horario,
                    sala=sala,
                    asiento=asiento,
                )
                for asiento in asientos_seleccionados
            ]
            db.session.add(reservacion)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                errores.append(
                    "Otro cliente acaba de reservar uno de esos asientos. "
                    "Actualiza el mapa y vuelve a elegir."
                )
                return render_template(
                    "reserva.html",
                    **contexto_reserva(errores, form_data, asientos_seleccionados),
                ), 409

            flash("¡Reservación guardada correctamente!", "success")
            return redirect(url_for("boleto", folio=reservacion.folio))

        return render_template(
            "reserva.html",
            **contexto_reserva(errores, form_data, asientos_seleccionados),
        )

    @app.get("/api/asientos")
    def asientos_funcion():
        pelicula = request.args.get("pelicula", "")
        fecha = request.args.get("fecha", "")
        horario = request.args.get("horario", "")
        sala = request.args.get("sala", "")
        try:
            fecha_valida = date.fromisoformat(fecha) >= date.today()
        except ValueError:
            fecha_valida = False
        if (
            pelicula not in PELICULAS
            or not fecha_valida
            or horario not in HORARIOS
            or sala not in SALAS
        ):
            return jsonify(error="Selecciona película, fecha, horario y sala válidos."), 400

        ocupados = db.session.execute(db.select(AsientoReservado.asiento).where(
            AsientoReservado.pelicula == pelicula,
            AsientoReservado.fecha == fecha,
            AsientoReservado.horario == horario,
            AsientoReservado.sala == sala,
        )).scalars().all()
        return jsonify(
            filas=FILAS_ASIENTOS,
            asientos_por_fila=ASIENTOS_POR_FILA,
            ocupados=ocupados,
            disponibles=len(ASIENTOS_DISPONIBLES) - len(ocupados),
        )

    @app.get("/boleto/<string:folio>")
    def boleto(folio):
        reservacion = db.session.execute(
            db.select(Reservacion).where(Reservacion.folio == folio.upper())
        ).scalar_one_or_none()
        if reservacion is None:
            abort(404)
        pelicula = next(
            item for item in cartelera_para_vista()
            if item["titulo"] == reservacion.pelicula
        )
        return render_template(
            "boleto.html", reservacion=reservacion, pelicula=pelicula
        )

    @app.route("/reservaciones")
    def listado():
        q = request.args.get("q", "").strip()
        if q:
            termino = f"%{q}%"
            consulta = db.select(Reservacion).where(or_(
                Reservacion.nombre.ilike(termino),
                Reservacion.correo.ilike(termino),
                Reservacion.pelicula.ilike(termino),
                Reservacion.folio.ilike(termino),
            ))
        else:
            consulta = db.select(Reservacion)
        reservaciones = db.session.execute(
            consulta.order_by(Reservacion.id.desc())
        ).scalars().all()
        total = db.session.scalar(
            db.select(db.func.count()).select_from(Reservacion)
        )
        return render_template("listado.html", reservaciones=reservaciones, q=q, total=total)

    @app.route("/cancelar/<int:reserva_id>", methods=["POST"])
    def cancelar(reserva_id):
        reservacion = db.session.get(Reservacion, reserva_id)
        if reservacion is not None:
            db.session.delete(reservacion)
            db.session.commit()
            flash("La reservación fue cancelada.", "info")
        else:
            flash("No se encontró esa reservación.", "error")
        return redirect(url_for("listado"))

    @app.route("/salud")
    def salud():
        db.session.execute(db.select(1))
        return {"estado": "correcto", "aplicacion": "CineFlix"}

    with app.app_context():
        db.create_all()
        columnas_reservaciones = {
            columna["name"]
            for columna in inspect(db.engine).get_columns("reservaciones")
        }
        if "folio" not in columnas_reservaciones:
            db.session.execute(
                text("ALTER TABLE reservaciones ADD COLUMN folio VARCHAR(12)")
            )
            db.session.commit()

        folios_vacios = db.session.execute(
            text("SELECT id FROM reservaciones WHERE folio IS NULL")
        ).scalars().all()
        for reserva_id in folios_vacios:
            db.session.execute(
                text("UPDATE reservaciones SET folio = :folio WHERE id = :id"),
                {"folio": secrets.token_hex(6).upper(), "id": reserva_id},
            )
        db.session.execute(text(
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_reservaciones_folio_idx "
            "ON reservaciones (folio)"
        ))
        db.session.commit()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", "5002")))
