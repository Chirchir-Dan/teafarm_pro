#!/usr/bin/env bash
# Removes pyc files and all pycache directories
# Adds all modified, untracked files then prompts for
# commit message and the branch then pushes to github
find . -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -r {} +


#git add .
#echo Enter commit message
#read message 
# git commit -m "$message"
# echo Which branch
# read branch
# git push origin $branch"""
