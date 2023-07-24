from random import randint, choice # For Fischer Random


sqrs = [(f,r) for f in range(8) for r in range(8)]


def get_start_pos(fischer_random=False):

    start_pos = [
        ['r+','n-','b-','q-','k+','b-','n-','r+'],
        ['p-','p-','p-','p-','p-','p-','p-','p-'],
        ['--','--','--','--','--','--','--','--'],
        ['--','--','--','--','--','--','--','--'],
        ['--','--','--','--','--','--','--','--'],
        ['--','--','--','--','--','--','--','--'],
        ['P-','P-','P-','P-','P-','P-','P-','P-'],
        ['R+','N-','B-','Q-','K+','B-','N-','R+']
    ]

    if not fischer_random: return start_pos

    files = [f for f in range(8)]

    # King
    kf = randint(1,6)
    start_pos[0][kf] = 'k+'
    files.remove(kf)

    # King-side rook
    r = randint(kf+1,7)
    start_pos[0][r] = 'r+'
    files.remove(r)

    # Queen-side rook
    r = randint(0,kf-1)
    start_pos[0][r] = 'r+'
    files.remove(r)

    # Bishops
    for i in range(2):
        b = choice([f for f in files if f%2==i])
        start_pos[0][b] = 'b-'
        files.remove(b)

    # Knights
    for i in range(2):
        n = choice(files)
        start_pos[0][n] = 'n-'
        files.remove(n)

    # Queen
    q = files[0]
    start_pos[0][q] = 'q-'

    for f, piece in enumerate(start_pos[0]):
        start_pos[7][f] = piece.upper()

    return start_pos


def is_enemy (is_white: bool, sqr: tuple, pos: list) -> bool:

    file, rank = sqr
    p = pos[rank][file][0]

    if p == '-': return False # Empty square
    if is_white and p.isupper(): return False
    if not is_white and p.islower(): return False

    return True


def is_friend(is_white: bool, sqr: tuple, pos: list) -> bool:

    file, rank = sqr
    p = pos[rank][file][0]

    if p == '-': return False # Empty square
    if is_white and p.islower(): return False
    if not is_white and p.isupper(): return False

    return True


def king_in_check   (is_white: bool, pos: list) -> bool:

    enemy_sqrs = []

    for sqr in sqrs:

        f,r = sqr
        p = pos[r][f][0]

        if is_enemy(is_white, sqr, pos):
            enemy_sqrs += get_squares(sqr, pos, legal=False)

        elif p.upper() == 'K':
            king_pos = sqr
    
    return king_pos in enemy_sqrs


def can_castle_short(is_white: bool, pos: list) -> bool:

    back_rank = 7 if is_white else 0
    king = 'K+' if is_white else 'k+'
    rook = 'R+' if is_white else 'r+'

    king_file = pos[back_rank].index(king)

    # Check that king-side rook has not moved or been captured
    try: rook_file = pos[back_rank][king_file:].index(rook)+king_file
    except ValueError: return False

    # All squares between king and king-side rook + f and g files are empty
    # (not including king and king-side rook)
    files = [f for f in range(king_file+1, rook_file)]+[5,6]
    for f in files:
        if   pos[back_rank][f] == rook and f == rook_file: pass
        elif pos[back_rank][f] == king: pass
        elif pos[back_rank][f] != '--': return False

    # King not currently in check or would be caslting through check
    files = [f for f in range(king_file, 7)]
    for f in files:

        new_pos = [row[:] for row in pos] # Make copy of position
        new_pos[back_rank][f] = '--' # Move king to new square
        new_pos[back_rank][f] = king[0]+'-'

        if king_in_check(is_white, new_pos): return False

    # Passed all checks
    return True


def can_castle_long (is_white: bool, pos: list) -> bool:

    back_rank = 7 if is_white else 0
    king = 'K+' if is_white else 'k+'
    rook = 'R+' if is_white else 'r+'

    king_file = pos[back_rank].index(king)

    # Check that queen-side rook has not moved or been captured
    try: rook_file = pos[back_rank][:king_file].index(rook)
    except ValueError: return False

    # All squares between king and queen-side rook + c and d files are empty
    # (not including king and queen-side rook)
    files = [f for f in range(rook_file+1, king_file)]+[2,3]
    for f in files:
        if   pos[back_rank][f] == rook and f == rook_file: pass
        elif pos[back_rank][f] == king: pass
        elif pos[back_rank][f] != '--': return False

    # King not currently in check or would be caslting through check
    lower = min(king_file,2)
    upper = max(king_file,2)

    files = [f for f in range(lower, upper+1)]
    for f in files:

        new_pos = [row[:] for row in pos] # Make copy of position
        new_pos[back_rank][f] = '--' # Move king to new square
        new_pos[back_rank][f] = king[0]+'-'

        if king_in_check(is_white, new_pos): return False

    # Passed all checks
    return True


def get_squares(sqr: tuple, pos: list, legal=True) -> list:

    a = [] # List of squares

    file, rank = sqr
    piece = pos[rank][file]

    is_white = piece[0].isupper()
    pawn_direction = -1 if is_white else 1


    distance, direction = {
        'K': (1, [(1,0), (0, 1), (-1,0), ( 0,-1), (1, 1), (1,-1), (-1, 1), (-1,-1)]),
        'Q': (7, [(1,0), (0, 1), (-1,0), ( 0,-1), (1, 1), (1,-1), (-1, 1), (-1,-1)]),
        'R': (7, [(1,0), (0, 1), (-1,0), ( 0,-1)]),
        'B': (7, [(1,1), (1,-1), (-1,1), (-1,-1)]),
        'N': (1, [(1,2), (2, 1), (-1,2), (-2, 1), (1,-2), (2,-1), (-1,-2), (-2,-1)]),
        'P': (1, [(1,pawn_direction), (-1,pawn_direction)])
    }[piece[0].upper()]

    for df, dr in direction:

        for m in range(1, distance+1):

            f,r = file+df*m, rank+dr*m

            if not (0 <= f <= 7 and 0 <= r <= 7): break # Out of bounds
            a.append((f,r))
            if pos[r][f][0] != '-': break # Square occupied


    if legal is False: return a


    if piece in ['P-', 'p-']:

        a = []
        start_rank = 6 if is_white else 1
        pawn_direction = -1 if is_white else 1

        # Captures/en passant
        for f,r in [(file-1, rank+pawn_direction), (file+1, rank+pawn_direction)]:

            if not (0 <= f <= 7 and 0 <= r <= 7): continue # Out of bounds
            p = pos[r][f]
            # Square occupied or en passant square
            if p != '--' or p == '-e': a.append((f,r))

        # Moving one/two squares ahead
        for i in range(2 if rank == start_rank else 1):

            f,r = file, rank+(i+1)*pawn_direction
            if pos[r][f][0] != '-': break # Square occupied
            a.append((f,r))


    # Remove illegal moves
    for f,r in a[:]:

        if is_friend(is_white, (f,r), pos):
            a.remove((f,r))
            continue

        new_pos = [row[:] for row in pos]
        new_pos[rank][file] = '--'
        new_pos[r][f] = piece[0]+'-'

        if king_in_check(is_white, new_pos):
            a.remove((f,r))


    if piece not in ['K+', 'k+']: return a


    if can_castle_short(is_white, pos):
        a.append((6,7 if is_white else 0))

    if can_castle_long(is_white, pos):
        a.append((2,7 if is_white else 0))

    return a
