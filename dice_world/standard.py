import json

txt_board_storeroom = {}


class JsonResponse:
    '''
        {'state':0,'msg':'xxxx', 'data': 'JsonObj'}
    '''

    def __init__(self, state, msg=None, data=None):
        self.state = state
        self.msg = str(msg)
        self.data = data

    def __str__(self):
        res = {}
        res['state'] = self.state
        if self.msg:
            res['msg'] = self.msg
        if self.data:
            res['data'] = json.dumps(self.data)
        return json.dumps(res)
