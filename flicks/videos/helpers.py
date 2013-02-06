from random import choice, randint

from jingo import register


@register.function
def admin_email_signature():
    salute = choice(['Cheers!', 'Engage,', 'Excelsior!', 'Carry on,',
                     'See you space cowboy...', 'STEVE HOLT,',
                     'Great shot kid, that was one in a million!'])
    rank = choice(['Junior', 'Senior', 'Head', 'Lead'])
    role = choice(['Commandant', 'Subcommander', 'Magistrate', 'Scribe',
                   'Attendant', 'Luthier', 'Codesmith', 'Director', 'Pilot'])
    num = randint(0, 1024)
    division = choice(['', ', Civilian Corps.', ', Eastern Operations',
                       ', Red Squadron',
                       ', Order of the Northern Sky (Hokuten)'])
    return ('{0}\n-{1} {2} #{3} of The Most Glorious and Excellent Flicks '
            'Collective{4}'.format(salute, rank, role, num, division))
