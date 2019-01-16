import csv
import urllib.request
from cs50 import SQL
from flask import redirect, render_template, request, session
from functools import wraps

def recipe():
    if request.method == "POST":
        title = request.method.get("title")
        bio = request.method.get("bio")
        tages = request.method.get("tags")

