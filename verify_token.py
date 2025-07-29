import requests

def verify_token(token):
    try:
        # 构建请求头，添加Bearer前缀
        headers = {'Authorization': f'Bearer {token}'}
        
        # 发送测试请求
        response = requests.get('https://api.inaturalist.org/v1/observations', headers=headers)
        
        # 打印响应信息
        print('响应状态码:', response.status_code)
        
        if response.status_code == 200:
            print('令牌验证成功！')
            return True
        else:
            print('令牌验证失败')
            print('错误信息:', response.text)
            return False
            
    except Exception as e:
        print('发生错误:', str(e))
        return False

if __name__ == '__main__':
    # 要验证的令牌
    token = 'eyJhbGciOiJIUzUxMiJ9.eyJ1c2VyX2lkIjo3NTA4ODg0LCJleHAiOjE3NTE3Mjg4MTB9.PwL9XbiY7CHkLfC7p9CIKUAkSo82VRx8DUxqU4WRVC_3H0gyL0mgw9m3flOwPKBzi9zFkX4e-jYQ3QBMLE11Pg'
    
    # 验证令牌
    verify_token(token)