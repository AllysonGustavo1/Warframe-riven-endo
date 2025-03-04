import requests
import math

def calculate_endo(mastery_rank, mod_rank, rerolls):
    """
    Calcula o valor de Endo baseado na fórmula fornecida.

    Args:
    mastery_rank (int): O Mastery Rank mínimo do item.
    mod_rank (int): O nível do mod.
    rerolls (int): O número de rerolls.

    Returns:
    int: O valor calculado de Endo.
    """
    endo = (100 * (mastery_rank - 8)) + abs(22.5 * (2 ** mod_rank)) + (200 * rerolls) - 7
    return math.floor(endo)

def fetch_auctions():
    """Busca os dados da API do Warframe Market."""
    url = "https://api.warframe.market/v1/auctions"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "language": "en",
        "platform": "pc"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro: {response.status_code} - {response.text}")
        return None

def process_auctions(data, option, max_mastery, seller_status):
    """Processa os leilões baseados na opção selecionada, nível de maestria e status do vendedor."""
    endo_plat_list = []

    for auction in data.get("payload", {}).get("auctions", []):
        item = auction.get("item", {})
        mastery_level = item.get("mastery_level", 0)
        if mastery_level > max_mastery:
            continue
        
        seller = auction.get("owner", {})
        seller_state = seller.get("status", "offline")
        
        if seller_status == "In-Game" and seller_state != "ingame":
            continue
        if seller_status == "Online" and seller_state not in ["online", "ingame"]:
            continue
        if seller_status == "Both" and seller_state not in ["online", "ingame"]:
            continue
        
        rerolls = item.get("re_rolls", 0)
        buyout_price = auction.get("buyout_price")
        starting_price = auction.get("starting_price")
        mod_rank = item.get("mod_rank", 0)
        auction_id = auction.get("id")
        endo_value = calculate_endo(mastery_level, mod_rank, rerolls)

        if option in ["Both", "Buyout"] and buyout_price and buyout_price > 0:
            endo_per_plat = endo_value / buyout_price
            endo_plat_list.append(("Buyout Price", endo_per_plat, rerolls, buyout_price, auction_id))
        if option in ["Both", "Starting"] and starting_price and starting_price > 0:
            endo_per_starting_price = endo_value / starting_price
            endo_plat_list.append(("Starting Price", endo_per_starting_price, rerolls, starting_price, auction_id))

    return sorted(endo_plat_list, key=lambda x: x[1], reverse=True)[:10]

def display_results(results):
    """Exibe os resultados formatados."""
    for entry in results:
        endo_total = entry[1] * entry[3]
        print(f"{entry[0]} Endo/Plat: {entry[1]:.2f}")
        print(f"Endo Total: {endo_total:.2f}")
        print(f"Rerolls: {entry[2]}")
        print(f"{entry[0]}: {entry[3]} platinum")
        print(f"Link: https://warframe.market/auction/{entry[4]}")
        print("-" * 30)

def main():
    """Menu principal do programa."""
    max_mastery = int(input("Digite seu nível de maestria: "))
    
    print("Selecione uma opção:")
    print("1 - Starting Price")
    print("2 - Buyout Price")
    print("3 - Ambos")

    option_map = {
        "1": "Starting",
        "2": "Buyout",
        "3": "Both"
    }

    choice = input("Escolha (1/2/3): ")
    option = option_map.get(choice)

    if not option:
        print("Opção inválida!")
        return
    
    print("Selecione o status do vendedor:")
    print("1 - In-Game")
    print("2 - Online")
    print("3 - Ambos")
    
    status_map = {
        "1": "In-Game",
        "2": "Online",
        "3": "Both"
    }
    
    status_choice = input("Escolha (1/2/3): ")
    seller_status = status_map.get(status_choice)
    
    if not seller_status:
        print("Opção inválida!")
        return

    data = fetch_auctions()
    if data:
        results = process_auctions(data, option, max_mastery, seller_status)
        display_results(results)

if __name__ == "__main__":
    main()
