#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2021-2022  Christopher Horn
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
ZoteroBibTex class
"""

# -------------------------------------------------------------------------
#
# Python Modules
#
# -------------------------------------------------------------------------
import json
import urllib.request
from urllib.error import URLError


# -------------------------------------------------------------------------
#
# ZoteroBibTex Class
#
# This is a simple class that makes use of the Better BibTex extension for
# the Zotero client to fetch citation and source information. Much more
# could be done interfacing with Zotero directly but this was quick to
# implement and seems sufficient for now.
#
# https://retorque.re/zotero-better-bibtex/installation/
# https://github.com/retorquere/zotero-better-bibtex
#
# -------------------------------------------------------------------------
class ZoteroBibTex:
    """
    Interfaces with a local Zotero client through the Better BibTex extension.
    """

    def __init__(self, base_url="http://localhost:23119/better-bibtex"):
        self.base_url = base_url

    def _get(self, endpoint, timeout=600):
        """
        GET data.
        """
        target = "%s/%s" % (self.base_url, endpoint)
        with urllib.request.urlopen(target, timeout=timeout) as response:
            data = response.read().decode("utf-8")
        return data

    def _post(self, endpoint, data):
        """
        POST data.
        """
        if isinstance(data, str):
            payload = data.encode("utf-8")
        else:
            payload = json.dumps(data).encode("utf-8")
        target = "%s/%s" % (self.base_url, endpoint)
        request = urllib.request.Request(target, data=payload, method="POST")
        request.add_header("Content-Type", "application/json")
        request.add_header("Accept", "application/json")
        with urllib.request.urlopen(request) as response:
            data = response.read().decode("utf-8")
        return data

    def ping(self):
        """
        Check BibTeX online and available.
        """
        endpoint = "cayw?probe=true"
        try:
            data = self._get(endpoint, timeout=0.1)
        except URLError:
            return False
        if data == "ready":
            return True
        return False

    def get_pick_data(self, minimize=True, detail=True):
        """
        Pick a citation.
        """
        if self.ping():
            endpoint = "cayw?format=json&minimize={}".format(
                str(minimize).lower()
            )
            pick = self._get(endpoint)
            if pick:
                citation = json.loads(pick)[0]
                if detail and "citekey" in citation:
                    source = self.get_source_data(citation["citekey"])
                    notes = self.get_note_data(citation["citekey"])
                else:
                    source = None
                    notes = None
                return citation, source, notes
        return None, None, None

    def get_source_data(self, citekey):
        """
        Get source from export based on citekey.
        """
        try:
            export = self.get_export([citekey])
        except URLError:
            return None
        try:
            data = json.loads(export)
            source = json.loads(data["result"][2])[0]
        except json.JSONDecodeError:
            return None
        return source

    def get_note_data(self, citekey):
        """
        Return note data based on citekey.
        """
        try:
            result = self.get_notes([citekey])
        except URLError:
            return None
        try:
            notes = json.loads(result)["result"][citekey]
        except json.JSONDecodeError:
            return None
        return notes

    def get_collections(self):
        """
        Get collections.
        """
        payload = {"jsonrpc": "2.0", "method": "user.groups"}
        return self._post("json-rpc", payload)

    def get_collection(self, collection_id, collection_format, notes=True):
        """
        Get export of a collection.
        """
        endpoint = "collection?%s.%s&exportNotes=%s" % (
            collection_id,
            collection_format,
            str(notes).lower(),
        )
        return self._get(endpoint)

    def get_notes(self, citekeys):
        """
        Get notes for a range of citekeys.
        """
        payload = {
            "jsonrpc": "2.0",
            "method": "item.notes",
            "params": [citekeys],
        }
        return self._post("json-rpc", payload)

    def get_attachments(self, citekey):
        """
        Get list of attachments for a given citekey.
        """
        payload = {
            "jsonrpc": "2.0",
            "method": "item.attachments",
            "params": [citekey],
        }
        return self._post("json-rpc", payload)

    def get_bibliography(self, citekeys, citeformat="json"):
        """
        Get bibliography for a list of citekeys.
        """
        payload = {
            "jsonrpc": "2.0",
            "method": "item.bibliography",
            "params": [citekeys, citeformat],
        }
        return self._post("json-rpc", payload)

    def get_export(self, citekeys, translator="json", library_id=1):
        """
        Generate an export for a list of citekeys.
        """
        payload = {
            "jsonrpc": "2.0",
            "method": "item.export",
            "params": [citekeys, translator, library_id],
        }
        return self._post("json-rpc", payload)
