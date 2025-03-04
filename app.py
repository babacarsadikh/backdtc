from datetime import date, datetime, timedelta
import decimal
import mysql.connector
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import json

# Initialisation de l'application Flask
app = Flask(__name__)
CORS(app)  # Activation de CORS pour les requêtes cross-origin

# Configuration de la base de données
# config = {
#     'user': 'sadikh',
#     'password': 'motdepasse',
#     'host': '50.62.180.5',
#     'database': 'districodbb'
# }
config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'dtcdbb'
}


# Fonction pour obtenir une connexion à la base de données
def get_db_connection():
    try:
        return mysql.connector.connect(**config)
    except mysql.connector.Error as err:
        print(f"Erreur de connexion à la base de données: {err}")
        raise

# Fonction de sérialisation personnalisée pour les types non JSON
def custom_serializer(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, timedelta):
        return str(obj)
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError(f"Type non sérialisable: {type(obj).__name__}")

# Fonction pour créer des réponses JSON
def create_json_response(data, status_code=200):
    return Response(
        json.dumps(data, default=custom_serializer),
        mimetype='application/json',
        status=status_code
    )

# Routes Adresses
@app.route('/adresses', methods=['GET'])
def get_adresses():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM AdressesChantier")
    adresses = cur.fetchall()
    cur.close()
    conn.close()
    return create_json_response({"status": "success", "data": adresses})

@app.route('/adresses', methods=['POST'])
def add_adresse():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO AdressesChantier (id_client, adresse) VALUES (%s, %s)", (data['id_client'], data['adresse']))
    conn.commit()
    cur.close()
    conn.close()
    return create_json_response({'status': 'success', 'message': 'Adresse ajoutée avec succès'})

# Routes Chauffeurs
@app.route('/chauffeurs', methods=['GET'])
def get_chauffeurs():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM Chauffeurs")
    chauffeurs = cur.fetchall()
    cur.close()
    conn.close()
    return create_json_response({"status": "success", "data": chauffeurs})
@app.route('/chauffeurs', methods=['POST'])
def add_chauffeur():
    try:
        data = request.json

        # Vérifier si toutes les clés nécessaires sont présentes
        required_keys = ['nom_chauffeur', 'telephone', 'plaque_camion']
        if not all(key in data for key in required_keys):
            return create_json_response({'status': 'error', 'message': 'Données incomplètes'}, 400)

        conn = get_db_connection()
        cur = conn.cursor()

        # Insérer les données dans la base de données
        cur.execute("""
            INSERT INTO Chauffeurs (nom_chauffeur, telephone, plaque_camion) 
            VALUES (%s, %s, %s)
        """, (data['nom_chauffeur'], data['telephone'], data['plaque_camion']))

        conn.commit()

        return create_json_response({'status': 'success', 'message': 'Chauffeur ajouté avec succès'})

    except KeyError as e:
        return create_json_response({'status': 'error', 'message': f'Champ manquant : {str(e)}'}, 400)

    except Exception as e:
        return create_json_response({'status': 'error', 'message': f'Erreur interne: {str(e)}'}, 500)

    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

# Route pour obtenir la liste des clients avec leurs adresses
@app.route('/clients', methods=['GET'])
def get_clients():
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        # Jointure entre Clients et AdressesChantier
        query = """
            SELECT c.id_client, c.nom_client, a.id_adresse, a.adresse
            FROM Clients c
            LEFT JOIN AdressesChantier a ON c.id_client = a.id_client
        """
        cur.execute(query)
        rows = cur.fetchall()

        # Organisation des données par client
        clients = {}
        for row in rows:
            client_id = row['id_client']
            if client_id not in clients:
                clients[client_id] = {
                    "id_client": client_id,
                    "nom_client": row.get("nom_client"),
                    "adresses": []
                }
            if row.get("id_adresse"):
                clients[client_id]["adresses"].append({
                    "id_adresse": row["id_adresse"],
                    "adresse": row["adresse"]
                })

        return create_json_response({"status": "success", "data": list(clients.values())})
    
    except Exception as e:
        return create_json_response({"status": "error", "message": str(e)}, 500)
    
    finally:
        cur.close()
        conn.close()

@app.route('/clients', methods=['POST'])
def add_client():
    try:
        data = request.json
        if not data.get('nom_client'):
            return create_json_response({"status": "error", "message": "Le nom du client est requis"}, 400)
        
        conn = get_db_connection()
        cur = conn.cursor()

        # Insérer le client
        cur.execute("INSERT INTO Clients (nom_client) VALUES (%s)", (data['nom_client'],))
        id_client = cur.lastrowid  # Récupérer l'ID du client inséré

        # Insérer l'adresse si elle est fournie
        if data.get('adresse'):
            cur.execute("INSERT INTO AdressesChantier (id_client, adresse) VALUES (%s, %s)", (id_client, data['adresse']))

        conn.commit()
        return create_json_response({"status": "success", "message": "Client et adresse ajoutés avec succès", "id_client": id_client})
    except Exception as e:
        conn.rollback()
        return create_json_response({"status": "error", "message": str(e)}, 500)
    finally:
        cur.close()
        conn.close()
# Route pour obtenir la liste des commandes
@app.route('/commandes', methods=['GET'])
def get_commandes():
    cur = None  # Initialiser la variable 'cur' avant l'utilisation
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        # Récupérer toutes les commandes
        cur.execute("""
            SELECT cmd.id_commande, cmd.id_client, cmd.formule, cmd.quantite_commandee, 
                   cmd.quantite_restante, cmd.date_production, c.nom_client
            FROM Commandes cmd
            JOIN Clients c ON cmd.id_client = c.id_client
        """)
        commandes = cur.fetchall()
        
        # Calculer la somme totale des quantités commandées
        cur.execute("SELECT SUM(quantite_commandee) AS total_quantite FROM Commandes")
        total_quantite = cur.fetchone()["total_quantite"]
        
        return create_json_response({
            "status": "success", 
            "length": len(commandes), 
            "total_quantite": total_quantite, 
            "data": commandes
        })
    except Exception as e:
        return create_json_response({"status": "error", "message": str(e)}, 500)
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# Route pour obtenir les commandes par date
@app.route('/commandes/date', methods=['GET'])
def get_commandes_by_date():
    date_param = request.args.get('date')
    if not date_param:
        return create_json_response({"status": "error", "message": "Date parameter is required"}, 400)
    
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        # Récupérer les commandes par date
        cur.execute("""
            SELECT cmd.id_commande, cmd.id_client, cmd.formule, cmd.quantite_commandee, 
                   cmd.quantite_restante, cmd.date_production, c.nom_client
            FROM Commandes cmd
            JOIN Clients c ON cmd.id_client = c.id_client
            WHERE DATE(cmd.date_production) = %s
        """, (date_param,))
        commandes = cur.fetchall()
        
        # Calculer la somme totale des quantités commandées pour cette date
        cur.execute("SELECT SUM(quantite_commandee) AS total_quantite FROM Commandes WHERE DATE(date_production) = %s", (date_param,))
        total_quantite = cur.fetchone()["total_quantite"]
        
        return create_json_response({
            "status": "success", 
            "length": len(commandes), 
            "total_quantite": total_quantite, 
            "data": commandes
        })
    except Exception as e:
        return create_json_response({"status": "error", "message": str(e)}, 500)
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()




# Route pour ajouter une commande
@app.route('/commandes', methods=['POST'])
def add_commande():
    try:
        data = request.json
        # Validation des données
        required_fields = ['id_client', 'formule', 'quantite_commandee', 'quantite_restante', 'date_production']
        if not all(field in data for field in required_fields):
            return create_json_response({"status": "error", "message": "Tous les champs sont requis"}, 400)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO Commandes (id_client, formule, quantite_commandee, quantite_restante, date_production) VALUES (%s, %s, %s, %s, %s)",
            (data['id_client'], data['formule'], data['quantite_commandee'], data['quantite_restante'], data['date_production'])
        )
        conn.commit()
        return create_json_response({"status": "success", "message": "Commande ajoutée avec succès"})
    except Exception as e:
        conn.rollback()  # Annulation en cas d'erreur
        return create_json_response({"status": "error", "message": str(e)}, 500)
    finally:
        cur.close()
        conn.close()

# Route pour obtenir la liste des livraisons
@app.route('/livraisons', methods=['GET'])
def get_livraisons():
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        # Récupérer les livraisons avec les détails clients et chauffeurs
        cur.execute("""
            SELECT l.*, c.nom_client, ch.nom_chauffeur, cmd.formule, ac.adresse, ch.plaque_camion
            FROM Livraisons l
            JOIN Commandes cmd ON l.id_commande = cmd.id_commande
            JOIN Clients c ON cmd.id_client = c.id_client
            JOIN Chauffeurs ch ON l.id_chauffeur = ch.id_chauffeur
            JOIN AdressesChantier ac ON l.id_adresse = ac.id_adresse
        """)
        livraisons = cur.fetchall()

        # Calculer la somme totale des quantités chargées
        cur.execute("SELECT SUM(quantite_chargee) AS total_quantite_chargee FROM Livraisons")
        total_quantite_chargee = cur.fetchone()["total_quantite_chargee"] or 0  # Évite les valeurs nulles

        return create_json_response({
            "status": "success",
            "length": len(livraisons),
            "total_quantite_chargee": total_quantite_chargee,
            "data": livraisons
        })

    except Exception as e:
        return create_json_response({"status": "error", "message": str(e)}, 500)
    finally:
        cur.close()
        conn.close()

@app.route('/livraisons/plage-dates', methods=['GET'])
def get_livraisons_by_date_range():
    date_debut = request.args.get('date_debut')
    date_fin = request.args.get('date_fin')

    # Vérification des paramètres
    if not date_debut or not date_fin:
        return create_json_response({"status": "error", "message": "Les paramètres 'date_debut' et 'date_fin' sont requis."}, 400)

    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        # Récupérer les livraisons dans la plage de dates spécifiée
        cur.execute("""
            SELECT l.*, c.nom_client, ch.nom_chauffeur, cmd.formule, ac.adresse, ch.plaque_camion
            FROM Livraisons l
            JOIN Commandes cmd ON l.id_commande = cmd.id_commande
            JOIN Clients c ON cmd.id_client = c.id_client
            JOIN Chauffeurs ch ON l.id_chauffeur = ch.id_chauffeur
            JOIN AdressesChantier ac ON l.id_adresse = ac.id_adresse
            WHERE DATE(l.date_production) BETWEEN %s AND %s
        """, (date_debut, date_fin))
        livraisons = cur.fetchall()


        # Calculer la somme totale des charges totales pour cette plage de dates
        total_charge = sum(livraison.get('quantite_chargee', 0) for livraison in livraisons)

        return create_json_response({
            "status": "success",
            "length": len(livraisons),
            "total_charge": total_charge,
            "data": livraisons
        })

    except Exception as e:
        return create_json_response({"status": "error", "message": str(e)}, 500)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# Route pour obtenir l'évolution des livraisons de la journée
@app.route('/livraisons/evolution', methods=['GET'])
def get_production_evolution():
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        # Récupérer l'évolution de la production par client
        cur.execute("""
            SELECT c.nom_client, (cmd.quantite_commandee) AS total_commandee, SUM(l.quantite_chargee) AS total_chargee
            FROM Livraisons l
            JOIN Commandes cmd ON l.id_commande = cmd.id_commande
            JOIN Clients c ON cmd.id_client = c.id_client
            GROUP BY c.nom_client
        """)
        production_data = cur.fetchall()
        
        return create_json_response({
            "status": "success",
            "data": production_data
        })
    except Exception as e:
        return create_json_response({"status": "error", "message": str(e)}, 500)
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

from flask import request
from datetime import datetime

@app.route('/livraisons/evolutionprime/plage-dates', methods=['GET'])
def get_production_evolution_plage_dates():
    try:
        # Récupérer les dates depuis les paramètres de la requête
        date_debut_str = request.args.get('date_debut')  # Format attendu : 'YYYY-MM-DD'
        date_fin_str = request.args.get('date_fin')

        if not date_debut_str or not date_fin_str:
            return create_json_response({"status": "error", "message": "Les paramètres 'date_debut' et 'date_fin' sont requis"}, 400)

        # Convertir les chaînes de dates en objets datetime
        try:
            date_debut = datetime.strptime(date_debut_str, '%Y-%m-%d').date()
            date_fin = datetime.strptime(date_fin_str, '%Y-%m-%d').date()
        except ValueError:
            return create_json_response({"status": "error", "message": "Format de date invalide. Utilisez 'YYYY-MM-DD'"}, 400)

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        # Récupérer l'évolution de la production par client pour la plage de dates spécifiée
        cur.execute("""
            SELECT c.nom_client, cmd.formule, ac.adresse, 
                   (cmd.quantite_commandee) AS total_commandee, 
                   SUM(l.quantite_chargee) AS total_chargee
            FROM Livraisons l
            JOIN Commandes cmd ON l.id_commande = cmd.id_commande
            JOIN Clients c ON cmd.id_client = c.id_client
            JOIN AdressesChantier ac ON l.id_adresse = ac.id_adresse
            WHERE DATE(l.date_production) BETWEEN %s AND %s
            GROUP BY c.nom_client, cmd.formule, ac.adresse
        """, (date_debut, date_fin))
        
        production_data = cur.fetchall()
          # Calculer la somme totale des quantités chargées
        cur.execute("SELECT SUM(quantite_chargee) AS total_quantite_chargee FROM Livraisons")
        total_quantite_chargee = cur.fetchone()["total_quantite_chargee"] or 0  # Évite les valeurs nulles

        return create_json_response({
            "status": "success",
            "total_charge": total_quantite_chargee,
            "data": production_data
        })

    except Exception as e:
        return create_json_response({"status": "error", "message": str(e)}, 500)
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@app.route('/livraisons/evolution/plage-dates', methods=['GET'])
def get_livraisons_by_date():
    date_debut = request.args.get('date_debut')
    date_fin = request.args.get('date_fin')

    if not date_debut or not date_fin:
        return create_json_response({"status": "error", "message": "Les paramètres 'date_debut' et 'date_fin' sont requis."}, 400)

    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        # Requête pour récupérer les livraisons avec leurs commandes associées
        cur.execute("""
            SELECT 
                c.nom_client, 
                cmd.id_commande, 
                cmd.formule, 
                cmd.quantite_commandee, 
                l.id_livraison, 
                l.quantite_chargee, 
                l.date_production, 
                ac.adresse 
            FROM Livraisons l
            JOIN Commandes cmd ON l.id_commande = cmd.id_commande
            JOIN Clients c ON cmd.id_client = c.id_client
            JOIN AdressesChantier ac ON l.id_adresse = ac.id_adresse
            WHERE DATE(l.date_production) BETWEEN %s AND %s
            ORDER BY c.nom_client, cmd.formule, cmd.id_commande, l.id_livraison
        """, (date_debut, date_fin))
        
        livraisons = cur.fetchall()

        # Regrouper les données par client et formule
        grouped_data = {}
        total_charge = 0
        commandes_vues = set()  # Pour éviter de cumuler plusieurs fois la même commande

        for livraison in livraisons:
            client = livraison["nom_client"]
            formule = livraison["formule"]
            id_commande = livraison["id_commande"]
            quantite_commandee = float(livraison["quantite_commandee"])  # Quantité commandée totale
            quantite_chargee = float(livraison["quantite_chargee"])

            if client not in grouped_data:
                grouped_data[client] = {}

            if formule not in grouped_data[client]:
                grouped_data[client][formule] = {
                    "total_commandee": 0.0,
                    "total_chargee": 0.0,
                    "livraisons": []
                }

            # Ajouter la quantité commandée UNIQUEMENT si on ne l'a pas encore prise pour cette commande
            if id_commande not in commandes_vues:
                grouped_data[client][formule]["total_commandee"] += quantite_commandee
                commandes_vues.add(id_commande)

            # Ajouter la quantité chargée
            grouped_data[client][formule]["total_chargee"] += quantite_chargee
            total_charge += quantite_chargee

            # Ajouter la livraison
            grouped_data[client][formule]["livraisons"].append({
                "id_livraison": livraison["id_livraison"],
                "quantite_commandee": quantite_commandee,  # Doit rester fixe par commande
                "quantite_chargee": quantite_chargee,
                "date_production": livraison["date_production"],
                "adresse": livraison["adresse"]
            })

        return create_json_response({
            "status": "success",
            "total_charge": total_charge,
            "length": len(livraisons),
            "data": grouped_data
        })

    except Exception as e:
        return create_json_response({"status": "error", "message": str(e)}, 500)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@app.route('/livraisons/evolution/date', methods=['GET'])
def get_production_evolution_date():
    try:
        # Récupérer la date depuis les paramètres de la requête
        date_str = request.args.get('date')  # Format attendu : 'YYYY-MM-DD'
        if not date_str:
            return create_json_response({"status": "error", "message": "Le paramètre 'date' est requis"}, 400)

        # Convertir la chaîne de date en objet datetime
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return create_json_response({"status": "error", "message": "Format de date invalide. Utilisez 'YYYY-MM-DD'"}, 400)

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        # Récupérer l'évolution de la production par client pour la date spécifiée
        cur.execute("""
            SELECT c.nom_client, (cmd.quantite_commandee) AS total_commandee, SUM(l.quantite_chargee) AS total_chargee
            FROM Livraisons l
            JOIN Commandes cmd ON l.id_commande = cmd.id_commande
            JOIN Clients c ON cmd.id_client = c.id_client
            WHERE DATE(l.date_production) = %s
            GROUP BY c.nom_client
        """, (date,))
        production_data = cur.fetchall()

        return create_json_response({
            "status": "success",
            "data": production_data
        })
    except Exception as e:
        return create_json_response({"status": "error", "message": str(e)}, 500)
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@app.route('/livraisons', methods=['POST'])
def add_livraison():
    try:
        data = request.json
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True, buffered=True)  # Ajout de buffered=True

        # Récupérer la quantité commandée et les détails du client à partir de la commande
        cur.execute("""
            SELECT cmd.quantite_commandee, cmd.quantite_restante, c.nom_client, a.adresse, cmd.formule
            FROM Commandes cmd
            JOIN Clients c ON cmd.id_client = c.id_client
            JOIN AdressesChantier a ON cmd.id_client = a.id_client
            WHERE cmd.id_commande = %s
        """, (data['id_commande'],))
        commande = cur.fetchone()
        
        # Assurer que tous les résultats sont consommés pour éviter l'erreur
        cur.fetchall()  

        if not commande:
            return create_json_response({'status': 'error', 'message': 'Commande non trouvée'})

        quantite_commandee = commande['quantite_commandee']
        quantite_restante_commande = commande['quantite_restante']

        # Calcul de la quantité totale chargée
        cur.execute("SELECT COALESCE(SUM(quantite_chargee), 0) AS total_charge FROM Livraisons WHERE id_commande = %s", (data['id_commande'],))
        total_charge_precedent = cur.fetchone()['total_charge']
        
        # Assurer que tous les résultats sont consommés pour éviter l'erreur
        cur.fetchall()  

        quantite_totale_chargee = total_charge_precedent + data['quantite_chargee']

        # Calcul de la nouvelle quantité restante
        quantite_restante = max(quantite_restante_commande - data['quantite_chargee'], 0)

        # Ajouter la livraison avec l'état initial 'en attente'
        cur.execute("""
            INSERT INTO Livraisons (id_commande, id_chauffeur, id_adresse, quantite_commandee, quantite_chargee, quantite_totale_chargee, quantite_restante, heure_depart, date_production, etat_livraison)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (data['id_commande'], data['id_chauffeur'], data['id_adresse'], quantite_commandee, data['quantite_chargee'], quantite_totale_chargee, quantite_restante, data['heure_depart'], data['date_production'], data.get('etat_livraison', 'en attente')))

        # Récupérer l'ID de la livraison nouvellement ajoutée
        id_livraison = cur.lastrowid

        # Ajout automatique du rapport avec les nouvelles informations
        cur.execute("""
            INSERT INTO Rapports (id_livraison, date_livraison, details_livraison) 
            VALUES (%s, %s, %s)
        """, (id_livraison, data['date_production'], f"Client: {commande['nom_client']}, Adresse Chantier: {commande['adresse']}, Formule: {commande['formule']}, Quantité Chargée: {data['quantite_chargee']} unités."))

        # Mise à jour de la quantité restante de la commande
        cur.execute("UPDATE Commandes SET quantite_restante = %s WHERE id_commande = %s", 
                    (quantite_restante, data['id_commande']))

        conn.commit()
        return create_json_response({'status': 'success', 'message': 'Livraison et rapport ajoutés avec succès'})
    
    except Exception as e:
        conn.rollback()
        return create_json_response({'status': 'error', 'message': str(e)})
    
    finally:
        cur.close()
        conn.close()

# Mettre à jour l'état de la livraison
@app.route('/livraisons/<int:id_livraison>/etat', methods=['PUT'])
def update_etat_livraison(id_livraison):
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE Livraisons SET etat_livraison = %s WHERE id_livraison = %s", (data['etat_livraison'], id_livraison))
    conn.commit()
    cur.close()
    conn.close()
    return create_json_response({'status': 'success', 'message': 'État de la livraison mis à jour avec succès'})

# Résumé des livraisons par jour
@app.route('/livraisons/summary', methods=['GET'])
def summary_livraisons():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT DATE(date_production) AS date, COUNT(*) AS total_livraisons, SUM(quantite_chargee) AS total_quantite
        FROM Livraisons
        GROUP BY DATE(date_production)
        ORDER BY DATE(date_production) DESC
    """)
    summary = cur.fetchall()
    cur.close()
    conn.close()
    return create_json_response({"status": "success", "data": summary})

# Routes Rapports
@app.route('/rapports', methods=['GET'])
def get_rapports():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM Rapports")
    rapports = cur.fetchall()
    cur.close()
    conn.close()
    return create_json_response({"status": "success", "data": rapports})

@app.route('/rapports', methods=['POST'])
def add_rapport():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO Rapports (id_livraison, date_livraison, details_livraison) VALUES (%s, %s, %s)",
                (data['id_livraison'], data['date_livraison'], data['details_livraison']))
    conn.commit()
    cur.close()
    conn.close()
    return create_json_response({'status': 'success', 'message': 'Rapport ajouté avec succès'})

# Démarrer l'application Flask
if __name__ == '__main__':
    app.run(debug=True)