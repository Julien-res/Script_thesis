#!/bin/sh
# -*- shell-script -*-
########################################################################
#  chargement de l'environnement utilisateur pour l'utilisation des
#  modules via :
#  - lmod
#  - easybuild
#  Utile en mode batch, en mode interactif l'environnement est chargé
#  automatiquement
########################################################################

lmod_env=/nfs/opt/apps/lmod/lmod.sh
easybuild_env=/nfs/opt/easybuild/env/easybuild.sh
if [ -f ${lmod_env} ]; then
    echo "loading lmod environment"
    . ${lmod_env}
fi
if [ -f ${easybuild_env} ]; then
    echo "loading easybuild environment"
    . ${easybuild_env}
fi
