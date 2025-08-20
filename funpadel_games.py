import streamlit as st
from datetime import datetime as dt
from functools import reduce
from math import floor
import random

current_day = dt.today().strftime("%d/%m/%Y")
st.title(f"🎾 Fun Games - {current_day} 🥎", width="content")
st.set_page_config(
    page_title=f"Fun Games - {current_day}", 
    page_icon="🎾",
    initial_sidebar_state="auto",
    layout="wide")

def main():
    with st.sidebar:
        raw_input = st.text_input(
            "Pf copia aqui a mensagem do grupo WhatsApp, depois de fechado:", 
            on_change=clean_session_state)
        # initialize_input(raw_input)
        st.button("Carregar mensagem", 
                  on_click=initialize_input(raw_input))

    if st.session_state.raw_input:
        women_list, men_list, fields_list = message_parse(st.session_state.raw_input)
        get_button_grid(len(women_list))

        initialize_fields_dict(len(fields_list))
        initialize_players(men_list, women_list)
        
        # Create Buttons
        cols_base = st.columns([3, 2], border=True, width=2000)

        with cols_base[0]:
            st.write("### Jogadoras: ###")
            cols = st.columns(st.session_state.grid_size_list[0])

            for n in range(st.session_state.grid_size_list[0]):
                for k in range(st.session_state.grid_size_list[1]):
                    with cols[n]:
                        st.button(f"{st.session_state.women_list_nested[n][k]}", 
                                on_click=on_button_click, 
                                kwargs={"button": st.session_state.women_list_nested[n][k]}, 
                                disabled=st.session_state.women_list_nested[n][k] in st.session_state.player_list_removed)

            st.write("### Jogadores: ###")
            cols = st.columns(st.session_state.grid_size_list[0])
            for n in range(st.session_state.grid_size_list[0]):
                for k in range(st.session_state.grid_size_list[1]):
                    with cols[n]:
                        st.button(f"{st.session_state.men_list_nested[n][k]}", 
                                on_click=on_button_click, 
                                kwargs={"button": st.session_state.men_list_nested[n][k]}, 
                                disabled=st.session_state.men_list_nested[n][k] in st.session_state.player_list_removed)

        if "last_clicked" in st.session_state:
            sel_player = st.session_state.last_clicked
            assign_players_to_field(sel_player, men_list, women_list)

            with cols_base[1]:
                st.write(f"Jogador Escolhido: **{st.session_state.last_clicked}**")
                st.write(f"Campo Atribuído: **{st.session_state.sel_field}**")
                st.session_state.current_fields = merge_dicts(st.session_state.field_dict_men, st.session_state.field_dict_women)

                for key in st.session_state.current_fields.keys():
                    players_merged = st.session_state.current_fields[key][0] + st.session_state.current_fields[key][1]
                    field_message = ', '.join([x for x in players_merged])
                    if len(players_merged) == 4:
                        field_message += " 🔒"
                    st.write(f"**Campo {key}**: {field_message}")

    return


def clean_session_state():
    for key in st.session_state.keys():
        del st.session_state[key]
    
    return


def initialize_input(raw_input):
    if "raw_input" not in st.session_state:
        st.session_state.raw_input = raw_input           

    return


def split_players_list(player_string_raw):
    # Separate by padel racket symbol
    player_split = player_string_raw.split("🎾 ")

    # Handle last player
    last_player = player_split[-1].split("🔒")[0]
    player_list = player_split[0:-1] + [last_player]

    # Remove trailing white spaces and capitalize
    player_list_cleaned = [x.strip().title() for x in player_list if len(x) > 1]
    return player_list_cleaned

def message_parse(message_raw):
    message_raw_clean = message_raw.lower().replace('\n', '')

    split0 = message_raw_clean.split("suplentes")
    try:
        spare_string_raw = split0[1]
    except IndexError:
        print("No Spare Players found")            

    split1 = split0[0].split("senhoras")
    women_string_raw = split1[1]

    split2 = split1[0].split("senhores")
    men_string_raw = split2[1]

    split3 = split2[0].split("cam")
    fields_list = [int(x) for x in split3[1].replace(' ', '').split(',')]

    women_list = split_players_list(women_string_raw)
    men_list = split_players_list(men_string_raw)

    return women_list, men_list, fields_list

def on_button_click(button):
    st.session_state.last_clicked = button
    remove_player_from_list(button)

    return

def initialize_fields_dict(n_fields):
    if "field_dict_men" not in st.session_state:
        field_dict_men = {}
        for field_id in range(n_fields):
            field_dict_men[field_id + 1] = []
        st.session_state.field_dict_men = field_dict_men

    if "field_dict_women" not in st.session_state:
        field_dict_women = {}
        for field_id in range(n_fields):
            field_dict_women[field_id + 1] = []
        st.session_state.field_dict_women = field_dict_women

    return

def factors(n):
    factors = set(reduce(
        list.__add__,
        ([i, n//i] for i in range(1, int(n**0.5) + 1) if n % i == 0)))
    
    return list(factors)

def get_button_grid(n_players):
    factors_n_players = factors(n_players)
    len_factors = len(factors_n_players)

    if len_factors % 2:
        # Odd number of factors - let's get the single middle one
        idx = int(floor(len_factors // 2))
        button_grid = [factors_n_players[idx], factors_n_players[idx]]
    else:
        # Even number of factors - let's get the two middle ones
        idx = int(floor(len_factors // 2) - 1)
        button_grid = [factors_n_players[idx], factors_n_players[idx + 1]]

    sorted_grid = sorted(button_grid, reverse=True)
    initialize_grid(sorted_grid)
    st.session_state.grid_size_list = sorted_grid

    return 

def flatten(nested_list):
    return [x for xs in nested_list for x in xs]

def reshape_list(flat_list, sizes):
    result = []
    index = 0
    rows, cols = sizes
    for _ in range(rows):
        row = flat_list[index:index+cols]
        result.append(row)
        index += cols
    return result

def get_current_fields(player_gender):
    if player_gender == 'men':
        current_fields = [x for x in st.session_state.field_dict_men.keys() if len(st.session_state.field_dict_men[x]) < 2]
        if len(current_fields):
            return current_fields
        else:
            # st.error(f"Atenção - Já não há campos disponíveis para os Jogadores: {st.session_state.field_dict_men}")
            pass
    elif player_gender == 'women':
        current_fields = [x for x in st.session_state.field_dict_women.keys() if len(st.session_state.field_dict_women[x]) < 2]
        if len(current_fields):
            return current_fields
        else:
            # st.error(f"Atenção - Já não há campos disponíveis para as Jogadoras: {st.session_state.field_dict_women}")
            pass
    return

def initialize_players(men_list, women_list):
    if "men_list" not in st.session_state:
        st.session_state.men_list = men_list
    men_list_nested = reshape_list(st.session_state.men_list, st.session_state.grid_size_list)

    if "women_list" not in st.session_state:
        st.session_state.women_list = women_list
    women_list_nested = reshape_list(st.session_state.women_list, st.session_state.grid_size_list)
        
    if "men_list_nested" not in st.session_state:
        st.session_state.men_list_nested = men_list_nested

    if "women_list_nested" not in st.session_state:
        st.session_state.women_list_nested = women_list_nested

    if "player_list_removed" not in st.session_state:
        st.session_state.player_list_removed = []

    return

def remove_player_from_list(player):
    # if player_gender == "men":
        # st.session_state.men_list_removed.append(player)
        # st.session_state.men_list.remove(player)
        # st.session_state.men_list_nested = [[subelt for subelt in elt if subelt != player] for elt in st.session_state.men_list_nested] 
    # elif player_gender == "women":
        # st.session_state.women_list_removed.append(player)
        # st.session_state.women_list.remove(player)
        # st.session_state.women_list_nested = [[subelt for subelt in elt if subelt != player] for elt in st.session_state.women_list_nested]
    st.session_state.player_list_removed.append(player)

    # st.write(st.session_state.player_list_removed)
    return    

def initialize_grid(grid_size_list):
    if "grid_size_list" not in st.session_state:
        st.session_state.grid_size_list = grid_size_list

    return

def assign_players_to_field(sel_player, men_list, women_list):
    initialize_field()

    assigned_players_list = flatten(list(st.session_state.field_dict_men.values()) + list(st.session_state.field_dict_women.values()))

    if sel_player not in assigned_players_list:
        if sel_player in men_list:
            # st.write("men")
            current_fields_men = get_current_fields("men")
            if current_fields_men:
                sel_field = random.choice(current_fields_men)
                st.session_state.field_dict_men[sel_field].append(sel_player)
            else:
                pass
        elif sel_player in women_list:
            # st.write("women")
            current_fields_women = get_current_fields("women")
            if current_fields_women:
                sel_field = random.choice(current_fields_women)
                st.session_state.field_dict_women[sel_field].append(sel_player)
            else:
                pass
        else:
            st.write("Nome não encontrado")
    
        st.session_state.sel_field = sel_field
    return st.session_state.sel_field


def initialize_field():
    if "sel_field" not in st.session_state:
        st.session_state.sel_field = None
    return

def merge_dicts(d1, d2):
    merged = {}
    for key in d1.keys():
        if key in d2:
            merged[key] = (d1[key], d2[key])  # or [d1[key], d2[key]]
        else:
            merged[key] = d1[key]
    # if d2 has extra keys not in d1
    for key in d2.keys() - d1.keys():
        merged[key] = d2[key]
    return merged

# v1 - Mobile improvements:
# Add a clear message button

# v2
# Allow change of fields
# Handle women playing in man's draw and vice-versa


if __name__ == "__main__":
    main()