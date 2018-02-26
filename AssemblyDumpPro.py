import sys

def getCredentials(isTest):
    from cryptography.fernet import Fernet
    clef = b'y1RrSzZel5RRjMjCZwwLVnVppKzqHQT0v-Mm96WNdS4='
    dataTest = b'gAAAAABZqXG7ztOFfBzQyWInJBGi2ug_TnFsZFLM0fbCCx6POD8ki_qCJRIlIm8jBh9Z918JxLi3He-46-rcoIZ_BgrwD9VvdYRA5_6G5k8FySU0m7qpPnV6UDh6ayqPlR-mvo8Dp3DTi8xElZVhp2tKtZBL95tl-5e2XtNsz67D1lkHui856v2G5jTh6zYNMS3ifjvnl1DQ0SuEKZ2FZay031QRu1q7Wg=='
    dataProd = b'gAAAAABZu4MLAoZXiIJnPwf-pn59_WKdt18um9Pn6K2AKOhT62GUsCXyDlFo4ArqrOnB08fL4p3ZJosIorRbllXa0mqOQiDTc7Bwv2Xneg3_UlN3z5hxR3sc8D2wNNiPcpoy3ofnr43e403TWulo60FOOAKr7mfWJSL8IpepcPVOWhv9CLltgvMHjqtmzJO621gKAtpuW2uYwv5dWx_VQXvSdDpoyl0SKw=='
    if isTest:
        data = dataTest
    else:
        data = dataProd
    import json
    cipher = Fernet(clef)
    creds = json.loads(cipher.decrypt(data).decode())
    creds = json.loads(cipher.decrypt(data).decode())
    creds =  {'user':'hp@maisonmoderne.lu', 'passwd':'Ubiclouder$2018','security_token':'ZI8DAzQdqx3ElEhliEarsEV5'}
    return creds



def processOut():

    from simple_salesforce import (
        Salesforce,
        SalesforceAPI,
        SFType,
        SalesforceError,
        SalesforceMoreThanOneRecord,
        SalesforceExpiredSession,
        SalesforceRefusedRequest,
        SalesforceResourceNotFound,
        SalesforceGeneralError,
        SalesforceMalformedRequest
    )
    isTest = False
    creds = getCredentials(isTest)
    
    sf = Salesforce(username=creds['user'], password=creds['passwd'], security_token=creds['security_token'], sandbox=isTest)
    print(dir(sf))
    fieldsToQuery =[]
    fieldsToExclude = []
    for t in  sf.Account.describe()['fields']:
        ''' Pour eviter les champ coumpoud: BillingAdrdress'''
        if t['compoundFieldName'] is not None and t['compoundFieldName'] not in fieldsToExclude:
            fieldsToExclude.append(t['compoundFieldName'])
    for t in  sf.Account.describe()['fields']:
        if t['name'] not in fieldsToExclude and t['calculated'] == False:
            fieldsToQuery.append(t['name'])

    queryAllAccount = 'select '+','.join(fieldsToQuery) +' from Account'
    cursor = sf.query_all(queryAllAccount)
    records =  cursor['records']
    i = 0
    import csv
    with open('./Account.csv','w') as f:
        fAccount =  csv.DictWriter(f,fieldnames=records[0].keys(),delimiter=';')
        print(fAccount)
        fAccount.writeheader()
        
        for r in records:
            print(fAccount.writerow(r))

    import json     
    with open('./resultat.json','w',encoding="utf-8") as js:   
        for rec in records:
            js.write( json.dumps(rec, ensure_ascii=False))            
    
    
def processIn():
    sf = Salesforce(username='hp@maisonmoderne.lu.1assembdev', password='Ubi$2018', security_token='KhrfeUNWQz8Z60PDIKG8G8vO', sandbox=true)
    import csv
    strFieldsToInsert="BillingStreet;BillingCity;BillingState;BillingPostalCode;BillingCountry;ShippingStreet;ShippingCity;ShippingState;ShippingPostalCode;ShippingCountry;Phone;Fax;Website;Cle_Client_STOCKX__;Name"
    fieldsToInsert  =strFieldsToInsert.split(';')
    batch =[]
    compteur = 0
    with open('./Account.csv','r') as inputF:
        data = csv.DictReader(inputF,delimter=';')
        for row in data:
            rec = {}
            for champ in fieldsToInsert:
                rec[champ]=row[champ]
            batch.append(rec)
            if len(batch)>=250:
                print('batch',compteur)
                sf.bulk.Account.insert(batch)
                batch=[]
                compteur +=1
        sf.bulk.Account.insert(batch)
        batch=[]
        print('all done', compteur)

        """
        attributes;Id;IsDeleted;MasterRecordId;Type;ParentId;BillingStreet;BillingCity;BillingState;BillingPostalCode;BillingCountry;BillingLatitude;BillingLongitude;
        BillingGeocodeAccuracy;
        
        ShippingStreet;ShippingCity;ShippingState;ShippingPostalCode;ShippingCountry;ShippingLatitude;ShippingLongitude;ShippingGeocodeAccuracy;Phone;Fax;Website;PhotoUrl;AnnualRevenue;NumberOfEmployees;Ownership;OwnerId;CreatedDate;CreatedById;LastModifiedDate;LastModifiedById;SystemModstamp;LastActivityDate;LastViewedDate;LastReferencedDate;Jigsaw;JigsawCompanyId;AccountSource;SicDesc;Numero_Client__c;Cle_Client_STOCKX__c;Typologie_Client__c;Pub_Possible__c;paperJam__c;City_Magazine_Print__c;Archiduc_Print__c;Cible_Audience__c;Registre_du_commerce__c;Clients_Prospect__c;Secteur_Activites_STX__c;Last_Contract_End_Date__c;Secteur_Activite_Cible__c;Merkur_Digital__c;Home_Sweet_Home__c;Mes_Remarques__c;Agence__c;Taux_de_Commission__c;Adresse_Mail__c;Num_ro_TVA__c;Secteur_Texte__c;Representant_Principal_STX__c;TVA_LUX__c;Status_Comptable__c;Periode_Communication__c;Cible_fonctions__c;Archiduc_Digital__c;Offre_Bouclage__c;Date_Creation_Societe__c;Delano_Print__c;HEX__c;Flydoscope_Print__c;Paperjam_Guide_Print__c;Explorator_Print__c;LCTO__c;Luxair__c;Business_Club_Member__c;Explorator_Digital__c;Business_Club_Live__c;paperJam_Digital__c;Delano_Digital__c;Family_Guide__c;Last_Contract_Start_Date__c;Contact_STX__c;Date_de_creation__c;Raison_sociale__c;Creation_STX__c;Merkur_Print__c;Secteur_activites_txt__c;Echange__c;Code_TVA__c;Land_Print__c;Descriptif__c;Complement_adresse__c;Montant_Facture_2016__c;Nom_Agence__c;Referent__c;Phone_2__c;Compte_Cloture__c;Export_to_STX__c;Centre_de_d_cision__c;Forme_juridique__c;Type__c;BE_2016__c;Objectif_2017__c;Montant_Facture_2017__c;Date_MAJ_Portefeuille_del__c;Date_MAJ_Portefeuille__c;MAJ_Portefeuille_OK__c;Paperjam_Dossiers_Digitaux__c;Commercial_PRINT__c;CA_Date__c;Ranking__c;Date_derni_re_activit__c;Statut_CLUB__c;CLUB_Statut_s_comment__c;Marques_Complices__c;CITY_BACKUP_AUDREY__c;Comptes_Dormants_2016__c;Conqu_te__c;Statut_Club_Date__c;BACKUP_AUDREY_AUTRES__c;Utilisateur_derni_re_modification__c;Type_de_public__c;Statut_Plan_M_dia_2016__c;Categorie_Sociaux_Professionnelle__c;Secteur_Activites_2__c;Montant_Facture_2014__c;Montant_Facture_2013__c;Montant_Facture_2012__c;Montant_Facture_2015__c;Date_de_derniere_modification__c;Linked_to2__c;Commercial_DGTL__c;Date_Statut_Plan_Media__c;Alias_Modification_Plan_Media__c;Commercial_Sponsoring__c;Secteurs_dactivite_GUIDE__c;Guide__c;Commercial_OP__c;A_facturer_Print_N__c;A_facturer_Print_N_1__c;A_facturer_Guide_N__c;A_facturer_Guide_N_1__c;Montant_Total_facturer_N__c;Montant_Total_facturer_N_1__c;A_facturer_DGTL_N__c;A_facturer_DGTL_N_1__c;A_facturer_Dossiers_Dgtx_N__c;A_facturer_Dossiers_Dgtx_N_1__c;A_facturer_CLUB_N__c;A_facturer_CLUB_N_1__c;A_facturer_Sponsoring_N__c;A_facturer_Sponsoring_N_1__c;A_facturer_OP_N__c;A_facturer_OP_N_1__c;A_facturer_PJ_Print_N__c;A_facturer_PJ_Print_N_1__c;A_facturer_DLN_Print_N__c;A_facturer_DLN_Print_N_1__c;A_facturer_CITY_Print_N__c;A_facturer_CITY_Print_N_1__c;A_facturer_MKR_Print_N__c;A_facturer_MKR_Print_N_1__c;A_facturer_FLYDO_Print_N__c;A_facturer_FLYDO_Print_N_1__c;A_facturer_HEX_Print_N__c;A_facturer_HEX_Print_N_1__c;A_facturer_ARCHI_Print_N__c;A_facturer_ARCHI_Print_N_1__c;A_facturer_LAND_Print_N__c;A_facturer_LAND_Print_N_1__c;Montant_facturer_2017_BE__c;Montant_facturer_2016_BE__c;Montant_facturer_2015_BE__c;R_f_rent_2017__c;Traitement_Assembly__c;Membership__c;Segmentation_2016__c;Lagence_est_deja_en_relation__c;Commentaire_Regie_Agence__c;Produit_2016__c;Produit_2017__c;Produit_unique_2016__c;Produit_unique_2017__c;Ancien_Membre__c;Commercial_unique__c;Workforce_Contrat__c;B_P__c;B_P_Code_Postal__c;B_P_Ville__c;Envoyer_B_P__c;X2018_BT_Montant_factur__c;Nombre_d_inscription__c;Nombre_de_participation__c;Participation_CLUB__c;Montant_Total_facturer_N_2__c;Membre_du_Club__c;Compte_VIrginie_2018__c;Profilage__c;Recruteur__c;Volume_recrutement_pige__c;Date_derni_re_annonce_PIGE__c;Credit_annuel_delano_JOBS__c;Credit_annuel_paperjam_JOBS__c;Consommation_Delano_JOBS__c;Consommation_Paperjam_JOBS__c;X2018_Segmentation__c;Date_derni_re_annonce_DLN__c;Date_prochain_anniversaire__c;Date_derniere_annonce_PJ__c;Sites_derni_res_annonces__c;Cr_dit_Membership_Paperjam__c;Cr_dit_Membership_Delano__c;Cle_Client_STX_GROUPE__c;Plan_Media_Id_al__c;Secteur_d_activit_de_l_offre__c;Approche_Commerciale__c;BE_N_GROUPE__c;BE_N_1_GROUPE__c;Segmentation_2017__c
        """
if __name__ == '__main__':
    ## processOut()
    processIn()
    