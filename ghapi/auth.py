# AUTOGENERATED! DO NOT EDIT! File to edit: 02_auth.ipynb (unless otherwise specified).

__all__ = ['GetAttrBase', 'GhDeviceAuth']

# Cell
from fastcore.utils import *
from .core import *

from urllib.parse import parse_qs

# Cell
_def_clientid = '771f3c3af93face45f52'

# Cell
class GetAttrBase:
    _attr=noop
    def __getattr__(self,k):
        if k[0]=='_' or k==self._attr: return super().__getattr__(k)
        return self._getattr(getattr(self, self._attr)[k])

    def __dir__(self): return custom_dir(self, getattr(self, self._attr))

# Cell
class GhDeviceAuth(GetAttrBase):
    "Get an oauth token using the GitHub API device workflow"
    _attr="params"
    def __init__(self, client_id=_def_clientid, *scopes):
        url = 'https://github.com/login/device/code'
        self.client_id = client_id
        self.params = parse_qs(urlread(url, client_id=client_id, scope=scope_str(scopes)))

    def _getattr(self,v): return v[0]

    def url_docs(self)->str:
        "Default instructions on how to authenticate"
        return f"""First copy your one-time code: {self.user_code}
Then visit {self.verification_uri} in your browser, and paste the code when prompted."""

    def open_browser(self):
        "Open a web browser with the verification URL"
        webbrowser.open(self.verification_uri)

    def auth(self)->str:
        "Return token if authentication complete, or `None` otherwise"
        resp = parse_qs(urlread(
            'https://github.com/login/oauth/access_token',
            client_id=self.client_id, device_code=self.device_code,
            grant_type='urn:ietf:params:oauth:grant-type:device_code'))
        err = nested_idx(resp, 'error', 0)
        if err == 'authorization_pending': return None
        if err: raise Exception(resp['error_description'][0])
        return resp['access_token'][0]

    def wait(self, cb:callable=None)->str:
        "Wait for authentication to complete, calling `cb` after each poll, if it is set"
        interval = int(self.interval)+1
        res = self.auth()
        while not res:
            if cb: cb()
            time.sleep(interval)
            res = self.auth()
        return res