def diff_user_input(user_input):
    for k in user_input.keys():
        user_input[k] = tuple(user_input[k].splitlines())
    gtin = user_input['gtin']
    kiz = user_input['kiz']
    tid = user_input['tid']

    if len(gtin) != len(kiz) or len(gtin) != len(tid) or len(kiz) != len(gtin) or len(kiz) != len(tid) \
            or len(tid) != len(gtin) or len(tid) != len(kiz):
        message = '<p style="color:red; text-align:center; margin:0;">Количество gtin, kiz и tid не совпадают</p>'
        return False, message

    user_input['kiz'] = list(zip(user_input.get('kiz'), user_input.get('tid')))

    count = 0
    for gtin in user_input.get('gtin'):
        user_input[gtin] = user_input.get('kiz')[count]
        count += 1

    for i in ['gtin', 'kiz', 'tid', 'email', 'product_type']:
        user_input.pop(i, None)

    return True, user_input
