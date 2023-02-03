import pwd


class Common:

    @staticmethod
    def round2(val):
        return round(val, 2)

    @staticmethod
    def read_file(file):
        file_obj = []
        with open(file, 'r') as f:
            file_obj = [line.split() for line in f]
        
        return file_obj

    @staticmethod
    def get_interval_vals(prev, curr, interval):
        try:
            return (float(curr) - float(prev)) / float(interval)
        except:
            return 0

    @staticmethod
    def get_user_name(uid):
        if uid == 0 or uid == '0':
            return "root"
        try:
            user_name = pwd.getpwuid(int(uid)).pw_name
        except Exception as ex:
            print(f"Could not find user_name for uid: {uid}. { ex }")
            user_name = ""

        return user_name

