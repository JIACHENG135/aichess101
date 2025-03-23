from mcts import Mct

initial_state = [
    ["红车", "红马", "红象", "红士", "红帅", "红士", "红象", "红马", "红车"],
    ["一一", "一一", "一一", "一一", "一一", "一一", "一一", "一一", "一一"],
    ["一一", "红炮", "一一", "一一", "一一", "一一", "一一", "红炮", "一一"],
    ["红兵", "一一", "红兵", "一一", "红兵", "一一", "红兵", "一一", "红兵"],
    ["一一", "一一", "一一", "一一", "一一", "一一", "一一", "一一", "一一"],
    ["一一", "一一", "一一", "一一", "一一", "一一", "一一", "一一", "一一"],
    ["黑兵", "一一", "黑兵", "一一", "黑兵", "一一", "黑兵", "一一", "黑兵"],
    ["一一", "黑炮", "一一", "一一", "一一", "一一", "一一", "黑炮", "一一"],
    ["一一", "一一", "一一", "一一", "一一", "一一", "一一", "一一", "一一"],
    ["黑车", "黑马", "黑象", "黑士", "黑帅", "黑士", "黑象", "黑马", "黑车"],
]

mct = Mct(initial_state)

while not mct.cur.state.is_terminal():
    mct.search()

    best_node = max(mct.cur.children.values(), key=lambda n: n.visits)

    print(f"AI 选择了动作: {best_node.state}")

    mct.cur = best_node
    mct.root = mct.cur
    mct.cur.parent = None

    opponent_action = get_player_move()
    next_state = best_node.state.apply_move(opponent_action)

    for child in mct.cur.children.values():
        if child.state == next_state:
            mct.cur = child
            mct.root = mct.cur
            mct.cur.parent = None
            break
    else:
        mct = Mct(next_state)
