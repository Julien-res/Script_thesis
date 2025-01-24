def create_settings(settings_path=None,input_path=None,output_path=None,resolution=20,):

    content = f"""inputfile={input_path}
    output={outputh_path}
    l2w_parameters=rhow_*"""
    
    try:
        with open(filepath, 'w') as file:
            file.write(content)
        print(f"Le fichier a été créé avec succès à l'emplacement : {filepath}")
    except Exception as e:
        print(f"Une erreur est survenue lors de la création du fichier : {e}")
