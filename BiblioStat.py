import streamlit
import streamlit as st
import streamlit_option_menu
import mysql.connector
import pandas as pd
import streamlit_authenticator
import plotly.express as px
# Etablir la connection à  MySQL database
connection = mysql.connector.connect(
    host="localhost",
    user="root",  # comme username par default
    password="",  # Par defaut vide
    database="biblio"
)

# Authentication
# Get user data
cursor = connection.cursor()
query = "SELECT nom, prenom, mail, password FROM utilisateurs"
cursor.execute(query)
result = cursor.fetchall()

# ================================= OUTILS D'AUTHENTIFICATION ==========================================

# Create user data dict
data = {"usernames": {}}
for row in result:
    username = row[1]  # prenom
    name = row[2]  # On utilise le mail pour plus d'unicité que le 'nom + prenom'
    email = row[2]
    password = row[3]

    data["usernames"][name] = {
        "name": name,
        "email": email,
        "password": password
    }

# Authentication
with streamlit.container():
    st.subheader("Bienvenue sur notre plateforme de gestion de bibliothèque.")

    authenticator = streamlit_authenticator.Authenticate(data, "library", "lb", 30)
    name, authenticator_status, username = authenticator.login("Login", "main")

if not authenticator_status:
    st.warning("Veuillez entrer les informations demandées")







# ===========================================================================================================================
# =============================== ICI COMMENCE L'APP SI authenticator_status renvoie vrai =======================================

elif authenticator_status:
    # Logout button
    authenticator.logout("Se deconnecter", "sidebar")


    # ==================================== FONCTIONS DE L'APPLICATION ==========================================

    # =============  FONCTION INSCRIPTION ==========

    def inscription():
        st.subheader("Inscription")
        nom = st.text_input("Votre nom")
        prenom = st.text_input("Votre Prenom")
        mail = st.text_input("Votre Adresse mail")
        role = st.selectbox("Rôle ", ("Admin", "Etudiant"))
        mpass = st.text_input("Votre mot de passe", type="password")
        mpass2 = st.text_input("Ressaisir le mot de passe", type="password")
        st.write("##")
        if st.button("S'inscrire"):
            if mpass != mpass2:
                st.error("Les mots de passe ne correspondent pas !")
            else:
                if nom and prenom and mail and mpass and role:
                    # Execute a query to check if the email exists in the database
                    query = "SELECT * FROM utilisateurs WHERE mail = %s"
                    # cursor.execute(query, (mail,))

                    # Fetch the first row from the result
                    # result = cursor.fetchone()
                    result = None  # Je met None parceque si result existe, ca veut dire que l'utilisateur existe deja
                    # dans la base de donnée. Mais quand tu vas enlever les commentaires pour faire ca facon sqlite
                    # result sera soi existant soi vide.

                    if result:
                        # If a matching record is found, display an error message
                        st.error("Utilisateur existant !")
                    else:
                        # ============= D'abord on hash le mdp avant d'ajouter le user maintenant
                        hashed_pw = streamlit_authenticator.Hasher([mpass]).generate()

                        # print("ICI JE FAIS DU MYSQL, A TOI DE MODIF POUR SQLITE")
                        # Execute the query with the corrected values list
                        values = (nom, prenom, mail, hashed_pw[0], role)  # Convert to tuple
                        query = "INSERT INTO Utilisateurs(Nom, Prenom, mail, password, Role) VALUES(%s, %s, %s, %s, %s)"
                        cursor.execute(query, values)
                        connection.commit()
                        st.success("Inscription réussie !")

                        # ================= ICI CE SERA CE BOUTON VALIDER QUI VA RECHARGER ============================
                        if st.button("Valider"):
                            inscription()
                else:
                    st.warning("Veuillez entrez tous les champs !")


    # =======================  FONCTION GESTION DE PROFIL ===========================================
    def gestion_profil():
        with streamlit.container():
            streamlit.subheader("Gestion de profil")

            # Rafraîchir les données avant de les afficher
            cursor.execute("SELECT nom, prenom, mail, password FROM Utilisateurs")
            result = cursor.fetchall()

            # Afficher les données dans un tableau
            if result:
                data_dict = {"Nom": [], "Prénom": [], "Mail": [], "Mot de passe": []}
                for row in result:
                    data_dict["Nom"].append(row[0])
                    data_dict["Prénom"].append(row[1])
                    data_dict["Mail"].append(row[2])
                    data_dict["Mot de passe"].append(row[3])

                st.table(pd.DataFrame(data_dict))
            else:
                st.warning("Aucun utilisateur trouvé.")
            # Ajouter un champ de texte pour entrer l'ID de l'utilisateur à supprimer
            user_id_to_delete = st.text_input("Entrez l'ID de l'utilisateur à supprimer", type="default")

            # Ajouter un bouton pour supprimer un utilisateur
            if st.button("Supprimer un Utilisateur"):
                try:
                    # Vérifier si l'ID existe dans la base de données
                    cursor.execute(f"SELECT * FROM Utilisateurs WHERE ID_utilisateur = {user_id_to_delete}")
                    existing_user = cursor.fetchone()

                    if existing_user:
                        # Exécuter la requête SQL pour supprimer l'utilisateur
                        delete_query = f"DELETE FROM Utilisateurs WHERE ID_utilisateur = {user_id_to_delete}"
                        cursor.execute(delete_query)

                        # Valider la suppression
                        connection.commit()
                        st.success("Utilisateur supprimé avec succès!")

                        # ============= ICI ENCORE J'EN RAJOUTE ========================

                        if st.button("Valider"):
                            gestion_profil()
                    else:
                        st.warning("L'ID de l'utilisateur n'existe pas.")
                except Exception as e:
                    st.error(f"Une erreur s'est produite lors de la suppression : {e}")

            # Fermer la connexion à la base de données
            # cursor.close()
            # connection.close()
            # Ajouter un champ de texte pour entrer l'ID de l'utilisateur à modifier
            user_id_to_modify = st.text_input("Entrez l'ID de l'utilisateur à modifier", type="default")

            # Ajouter des champs pour les nouvelles valeurs de l'utilisateur
            new_nom = st.text_input("Nouveau Nom", type="default")
            new_prenom = st.text_input("Nouveau Prénom", type="default")
            new_nom_utilisateur = st.text_input("Nouveau Nom d'utilisateur", type="default")
            new_role = st.selectbox("Nouveau Rôle", ['Etudiant', 'Admin'])
            new_mail = st.text_input("Nouveau Mail", type="default")

            # Ajouter un bouton pour modifier un utilisateur
            if st.button("Modifier un Utilisateur"):
                try:
                    # Vérifier si l'ID existe dans la base de données
                    cursor.execute(f"SELECT * FROM Utilisateurs WHERE ID_utilisateur = {user_id_to_modify}")
                    existing_user = cursor.fetchone()

                    if existing_user:
                        # Exécuter la requête SQL pour modifier l'utilisateur
                        update_query = f"UPDATE Utilisateurs SET Nom = '{new_nom}', Prenom = '{new_prenom}', " \
                                       f"Nom_utilisateur = '{new_nom_utilisateur}', Role = '{new_role}', " \
                                       f"mail = '{new_mail}' WHERE ID_utilisateur = {user_id_to_modify}"
                        cursor.execute(update_query)

                        # Valider la modification
                        connection.commit()

                        # ====================== ICI AUSSI ==================================

                        st.success("Utilisateur modifié avec succès!")
                        if st.button("Valider"):
                            gestion_profil()
                    else:
                        st.warning("L'ID de l'utilisateur n'existe pas.")
                except Exception as e:
                    st.error(f"Une erreur s'est produite lors de la modification : {e}")

            # Fermer la connexion à la base de données
            cursor.close()
            connection.close()


    # =======================  FONCTION GESTION DE Livre ===========================================
    def gestion_livres():
        st.subheader("Gestion de Livres")

        # Rafraîchir les données avant de les afficher
        cursor.execute(
            "SELECT ID_livre, Titre, Auteur, Annee_publication, Genre, Quantite_disponible, Autres_informations FROM Livres")
        result = cursor.fetchall()

        # Afficher les données dans un tableau
        if result:
            data_dict = {
                "ID Livre": [],
                "Titre": [],
                "Auteur": [],
                "Année de publication": [],
                "Genre": [],
                "Quantité disponible": [],
                "Autres informations": []
            }
            for row in result:
                data_dict["ID Livre"].append(row[0])
                data_dict["Titre"].append(row[1])
                data_dict["Auteur"].append(row[2])
                data_dict["Année de publication"].append(row[3])
                data_dict["Genre"].append(row[4])
                data_dict["Quantité disponible"].append(row[5])
                data_dict["Autres informations"].append(row[6])

            st.table(pd.DataFrame(data_dict))
        else:
            st.warning("Aucun livre trouvé.")

        # Section pour ajouter un livre
        st.subheader("Ajouter un Livre")
        titre = st.text_input("Titre (ajout)", key="ADD_titre")
        auteur = st.text_input("Auteur (ajout)", key="ajout_auteur")
        annee = st.text_input("Année de publication (ajout)", key="ajout_annee")
        genre = st.text_input("Genre (ajout)", key="ajout_genre")
        quantite = st.text_input("Quantité disponible (ajout)", key="ajout_quantite")
        informations = st.text_area("Autres informations (ajout)", key="ajout_informations")

        if st.button("Valider l'ajout"):
            try:
                # Exécuter la requête SQL pour ajouter le livre
                insert_query = f"INSERT INTO Livres (Titre, Auteur, Annee_publication, Genre, Quantite_disponible, Autres_informations) " \
                               f"VALUES ('{titre}', '{auteur}', {annee}, '{genre}', {quantite}, '{informations}')"
                cursor.execute(insert_query)

                # Valider l'ajout
                connection.commit()
                st.success("Livre ajouté avec succès!")

                # Rafraîchir la page
                if st.button("Valider"):
                    gestion_livres()
            except Exception as e:
                st.error(f"Une erreur s'est produite lors de l'ajout : {e}")

        # Section pour modifier un livre
        st.subheader("Modifier un Livre")
        livre_id_to_modify = st.text_input("Entrez l'ID du livre à modifier", type="default", key="modify_id")
        new_titre = st.text_input("Nouveau Titre (modif)", type="default", key="modify_titre")
        new_auteur = st.text_input("Nouvel Auteur (modif)", type="default", key="modify_auteur")
        new_annee = st.text_input("Nouvelle Année de publication (modif)", type="default", key="modify_annee")
        new_genre = st.text_input("Nouveau Genre (modif)", type="default", key="modify_genre")
        new_quantite = st.text_input("Nouvelle Quantité disponible (modif)", type="default", key="modify_quantite")
        new_informations = st.text_area("Nouvelles Informations (modif)", key="modify_informations")

        if st.button("Valider la modification"):
            try:
                # Vérifier si l'ID du livre existe dans la base de données
                cursor.execute(f"SELECT * FROM Livres WHERE ID_livre = {livre_id_to_modify}")
                existing_book = cursor.fetchone()

                if existing_book:
                    # Exécuter la requête SQL pour modifier le livre
                    update_query = f"UPDATE Livres SET Titre = '{new_titre}', Auteur = '{new_auteur}', " \
                                   f"Annee_publication = {new_annee}, Genre = '{new_genre}', " \
                                   f"Quantite_disponible = {new_quantite}, Autres_informations = '{new_informations}' " \
                                   f"WHERE ID_livre = {livre_id_to_modify}"
                    cursor.execute(update_query)

                    # Valider la modification
                    connection.commit()
                    st.success("Livre modifié avec succès!")

                    # Rafraîchir la page
                    if st.button("Valider"):
                        gestion_livres()
                else:
                    st.warning("L'ID du livre n'existe pas.")
            except Exception as e:
                st.error(f"Une erreur s'est produite lors de la modification : {e}")

        # Section pour supprimer un livre
        st.subheader("Supprimer un Livre")
        livre_id_to_delete = st.text_input("Entrez l'ID du livre à supprimer", type="default", key="delete_id")

        if st.button("Valider la suppression"):
            try:
                # Vérifier si l'ID du livre existe dans la base de données
                cursor.execute(f"SELECT * FROM Livres WHERE ID_livre = {livre_id_to_delete}")
                existing_book = cursor.fetchone()

                if existing_book:
                    # Exécuter la requête SQL pour supprimer le livre
                    delete_query = f"DELETE FROM Livres WHERE ID_livre = {livre_id_to_delete}"
                    cursor.execute(delete_query)

                    # Valider la suppression
                    connection.commit()
                    st.success("Livre supprimé avec succès!")

                    # Rafraîchir la page
                    if st.button("Valider"):
                        gestion_livres()
                else:
                    st.warning("L'ID du livre n'existe pas.")
            except Exception as e:
                st.error(f"Une erreur s'est produite lors de la suppression : {e}")

        # Fermer la connexion à la base de données
        cursor.close()
        connection.close()


    # =================================  FONCTION GESTION Etudiant/Admins ===========================================
    def gestion_etudiants_admins():
        st.subheader("Gestion des Étudiants et Administrateurs")

        # Rafraîchir les données avant de les afficher
        cursor.execute(
            "SELECT ID_utilisateur, Nom, Prenom, Mail, Role FROM Utilisateurs"
        )
        result = cursor.fetchall()

        # Afficher les données dans un tableau
        if result:
            data_dict = {
                "ID Utilisateur": [],
                "Nom": [],
                "Prénom": [],
                "Mail": [],
                "Role": []
            }
            for row in result:
                data_dict["ID Utilisateur"].append(row[0])
                data_dict["Nom"].append(row[1])
                data_dict["Prénom"].append(row[2])
                data_dict["Mail"].append(row[3])
                data_dict["Role"].append(row[4])

            etudiants_admins_df = pd.DataFrame(data_dict)
            st.table(etudiants_admins_df)
        else:
            st.warning("Aucun étudiant ou administrateur trouvé.")

        # Section pour ajouter un étudiant ou administrateur
        st.subheader("Ajouter un Étudiant ou Administrateur")
        nom = st.text_input("Nom (ajout)", key="ADD_nom")
        prenom = st.text_input("Prénom (ajout)", key="ajout_prenom")
        mail = st.text_input("Mail (ajout)", key="ajout_mail")
        role = st.selectbox("Rôle (ajout)", ["Etudiant", "Admin"], key="ajout_role")

        if st.button("Valider l'ajout"):
            try:
                # Exécuter la requête SQL pour ajouter l'étudiant ou administrateur
                insert_query = f"INSERT INTO Utilisateurs (Nom, Prenom, Mail, Role) " \
                               f"VALUES ('{nom}', '{prenom}', '{mail}', '{role}')"
                cursor.execute(insert_query)

                # Valider l'ajout
                connection.commit()
                st.success("Étudiant ou administrateur ajouté avec succès!")

                # Rafraîchir la page
                if st.button("Valider"):
                    gestion_etudiants_admins()
            except Exception as e:
                st.error(f"Une erreur s'est produite lors de l'ajout : {e}")

        # Section pour supprimer un étudiant ou administrateur
        st.subheader("Supprimer un Étudiant ou Administrateur")
        utilisateur_id_to_delete = st.text_input("Entrez l'ID de l'utilisateur à supprimer", type="default",
                                                 key="delete_id")

        if st.button("Valider la suppression"):
            try:
                # Vérifier si l'ID de l'utilisateur existe dans la base de données
                cursor.execute(f"SELECT * FROM Utilisateurs WHERE ID_utilisateur = {utilisateur_id_to_delete}")
                existing_user = cursor.fetchone()

                if existing_user:
                    # Exécuter la requête SQL pour supprimer l'utilisateur
                    delete_query = f"DELETE FROM Utilisateurs WHERE ID_utilisateur = {utilisateur_id_to_delete}"
                    cursor.execute(delete_query)

                    # Valider la suppression
                    connection.commit()
                    st.success("Étudiant ou administrateur supprimé avec succès!")

                    # Rafraîchir la page
                    if st.button("Valider"):
                        gestion_etudiants_admins()
                else:
                    st.warning("L'ID de l'utilisateur n'existe pas.")
            except Exception as e:
                st.error(f"Une erreur s'est produite lors de la suppression : {e}")

        # Fermer la connexion à la base de données
        cursor.close()
        connection.close()


    # ==================================== FONCTION GESTION DES LOCATIONS ==========================================
    def gestion_locations():
        # Etablir la connection à  MySQL database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",  # comme username par default
            password="",  # Par defaut vide
            database="biblio"
        )

        # Créer un curseur
        cursor = connection.cursor()

        st.subheader("Gestion des Locations")

        # Rafraîchir les données avant de les afficher
        cursor.execute(
            "SELECT L.ID_location, U.nom, U.prenom, U.mail, Li.Titre, L.Date_location, L.Date_retour_prevue, L.Statut FROM Locations L JOIN Utilisateurs U ON L.ID_etudiant = U.ID_utilisateur JOIN Livres Li ON L.ID_livre = Li.ID_livre")
        result = cursor.fetchall()

        # Afficher les données dans un tableau
        if result:
            data_dict = {
                "ID Location": [],
                "Nom": [],
                "Prénom": [],
                "Mail": [],
                "Titre": [],
                "Date de location": [],
                "Date de retour prévue": [],
                "Statut": []
            }
            for row in result:
                data_dict["ID Location"].append(row[0])
                data_dict["Nom"].append(row[1])
                data_dict["Prénom"].append(row[2])
                data_dict["Mail"].append(row[3])
                data_dict["Titre"].append(row[4])
                data_dict["Date de location"].append(row[5])
                data_dict["Date de retour prévue"].append(row[6])
                data_dict["Statut"].append(row[7])

            locations_df = pd.DataFrame(data_dict)
            st.table(locations_df)
        else:
            st.warning("Aucune location trouvée.")

        # Section pour ajouter une location
        st.subheader("Ajouter une Location")
        etudiant_id = st.text_input("ID de l'étudiant", type="default", key="add_location_student_id")
        livre_id = st.text_input("ID du livre", type="default", key="add_location_book_id")
        date_location = st.date_input("Date de location", key="add_location_start_date")
        date_retour_prevue = st.date_input("Date de retour prévue", key="add_location_return_date")
        statut = st.text_input("Statut", type="default", key="add_location_status")

        if st.button("Valider l'ajout"):
            try:
                # Exécuter la requête SQL pour ajouter la location
                insert_query = f"INSERT INTO Locations (ID_livre, ID_etudiant, Date_location, Date_retour_prevue, Statut) " \
                               f"VALUES ({livre_id}, {etudiant_id}, '{date_location}', '{date_retour_prevue}', '{statut}')"
                cursor.execute(insert_query)

                # Valider l'ajout
                connection.commit()
                st.success("Location ajoutée avec succès!")

                # Rafraîchir la page
                if st.button("Valider"):
                    gestion_locations()
            except Exception as e:
                st.error(f"Une erreur s'est produite lors de l'ajout : {e}")

        # Section pour supprimer une location
        st.subheader("Supprimer une Location")
        location_id_to_delete = st.text_input("Entrez l'ID de la location à supprimer", type="default",
                                              key="delete_location_id")

        if st.button("Valider la suppression"):
            try:
                # Vérifier si l'ID de la location existe dans la base de données
                cursor.execute(f"SELECT * FROM Locations WHERE ID_location = {location_id_to_delete}")
                existing_location = cursor.fetchone()

                if existing_location:
                    # Exécuter la requête SQL pour supprimer la location
                    delete_query = f"DELETE FROM Locations WHERE ID_location = {location_id_to_delete}"
                    cursor.execute(delete_query)

                    # Valider la suppression
                    connection.commit()
                    st.success("Location supprimée avec succès!")

                    # Rafraîchir la page
                    if st.button("Valider"):
                        gestion_locations()
                else:
                    st.warning("L'ID de la location n'existe pas.")
            except Exception as e:
                st.error(f"Une erreur s'est produite lors de la suppression : {e}")

        # Fermer la connexion à la base de données
        cursor.close()
        connection.close()


    # =========================================== FIN DES FONCTIONS ===================================================

    # Navigation menu
    with st.sidebar:
        st.image("logo.jpg", width=100)  # Remplacez "chemin_vers_votre_image/logo.png" par le chemin de votre image
        st.success(f"* BiblioStat, la bibliothèque des scientifiques")
        st.write("Bienvenue !")

        choice = streamlit_option_menu.option_menu(
            menu_title="Menu",
            options=["Inscription", "Gestion de profil", "Gestion des livres",
                     "Gestion étudiants/admins", "Gestion des locations",
                     "Dashboard"]
        )

    # ...

    if choice == "Inscription":
        """"""
        inscription()


    elif choice == "Gestion de profil":
        """"""
        gestion_profil()

    elif choice == "Gestion des livres":
        """"""
        gestion_livres()
    elif choice == "Gestion étudiants/admins":
        """"""
        gestion_etudiants_admins()
    elif choice == "Gestion des locations":
        """"""
        gestion_locations()
    elif choice == "Dashboard":
        """"""
        st.subheader("Dashboard")

        # Statistiques descriptives pour la répartition des genres de livres
        cursor.execute("SELECT Genre, COUNT(*) FROM Livres GROUP BY Genre")
        result_genre_counts = cursor.fetchall()

        if result_genre_counts:
            data_dict_genre_counts = {
                "Genre": [],
                "Nombre de livres": []
            }
            for row in result_genre_counts:
                data_dict_genre_counts["Genre"].append(row[0])
                data_dict_genre_counts["Nombre de livres"].append(row[1])

            genre_counts_df = pd.DataFrame(data_dict_genre_counts)

            # Exemple de graphique avec Plotly (bar chart)
            fig_genre_counts = px.bar(genre_counts_df, x='Genre', y='Nombre de livres',
                                      title='Répartition des livres par genre')
            st.plotly_chart(fig_genre_counts)

            # Affichage de la statistique descriptive
            st.write("Statistique descriptive pour la répartition des livres par genre :")
            for row in result_genre_counts:
                st.write(f"{row[0]} : {row[1]}")

            # Calcul des statistiques supplémentaires
            mean_genre, max_genre, min_genre = genre_counts_df["Nombre de livres"].mean(), genre_counts_df[
                "Nombre de livres"].max(), genre_counts_df["Nombre de livres"].min()
            st.write(f"Moyenne des livres par genre: {mean_genre}")
            st.write(f"Maximum des livres par genre: {max_genre}")
            st.write(f"Minimum des livres par genre: {min_genre}")

        else:
            st.warning("Aucun livre trouvé pour générer des statistiques.")

        # ...

        # Statistiques descriptives pour la répartition des utilisateurs par rôle
        cursor.execute("SELECT Role, COUNT(*) FROM Utilisateurs GROUP BY Role")
        result_role_counts = cursor.fetchall()

        if result_role_counts:
            data_dict_role_counts = {
                "Role": [],
                "Nombre d'utilisateurs": []
            }
            for row in result_role_counts:
                data_dict_role_counts["Role"].append(row[0])
                data_dict_role_counts["Nombre d'utilisateurs"].append(row[1])

            role_counts_df = pd.DataFrame(data_dict_role_counts)

            # Calcul des statistiques
            min_count = role_counts_df["Nombre d'utilisateurs"].min()
            max_count = role_counts_df["Nombre d'utilisateurs"].max()
            mean_count = role_counts_df["Nombre d'utilisateurs"].mean()

            # Exemple de graphique avec Plotly (camembert/pie chart)
            fig_role_counts = px.pie(role_counts_df, names='Role', values='Nombre d\'utilisateurs',
                                     title=f'Répartition des utilisateurs par rôle\nMin: {min_count}, Max: {max_count}, Moyenne: {mean_count}')
            st.plotly_chart(fig_role_counts)

            # Affichage de la statistique descriptive
            st.write("Statistique descriptive pour la répartition des utilisateurs par rôle :")
            st.write(f"Minimum : {min_count}")
            st.write(f"Maximum : {max_count}")
            st.write(f"Moyenne : {mean_count}")

            for row in result_role_counts:
                st.write(f"{row[0]} : {row[1]}")

        else:
            st.warning("Aucun utilisateur trouvé pour générer des statistiques.")



