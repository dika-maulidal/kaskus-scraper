import requests
from bs4 import BeautifulSoup
import csv
from tqdm import tqdm

def scrape_kaskus(user, iterations, output_file):
    base_url = f"https://www.kaskus.co.id/@{user}/viewallposts/?sort=desc"
    scraped_data = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }
    
    print(f"Scraping threads for user '@{user}'...")
    current_url = base_url
    with tqdm(total=iterations, desc="Scraping Progress") as pbar:
        while len(scraped_data) < iterations:
            response = requests.get(current_url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Scrape thread data
            threads = soup.find_all('div', class_='D(f) Ai(c) Jc(sb)')
            if not threads and len(scraped_data) == 0:  # Tidak ada thread sama sekali
                print("Tidak ada thread yang ditemukan untuk user ini.")
                return
            
            if not threads:  # Tidak ada thread lebih lanjut
                print("No more threads found!")
                break
            
            for thread in threads:
                if len(scraped_data) >= iterations:
                    break
                
                try:
                    title = thread.find('div', class_='Fw(500) C(c-primary) Fz(18px) Mb(8px)').text.strip()
                    content = thread.find('div', class_='C(c-secondary) Lh(1.5)').text.strip()
                    date_info = thread.find_previous('span', class_='Fz(12px) C(c-secondary)').text.strip()
                    replied_to = thread.find_previous('span', class_='C(c-secondary) Fw(500)').text.strip()
                    
                    scraped_data.append({
                        "Date": date_info,
                        "Replied To": replied_to,
                        "Thread Title": title,
                        "Post Content": content
                    })
                except AttributeError:
                    continue
            
            # Scrape Halaman Selanjutnya
            next_page = soup.find('a', text=str(len(scraped_data) // 20 + 1))  # Cari link ke halaman berikutnya (20 post per halaman)
            if next_page and 'href' in next_page.attrs:
                current_url = "https://www.kaskus.co.id" + next_page['href']
            else:
                print("No more pages found!")
                break
            
            pbar.update(min(iterations, len(scraped_data)) - pbar.n)  # Update loading bar

    # Simpan hasil ke file CSV jika ada data
    if scraped_data:
        with open(output_file, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=["Date", "Replied To", "Thread Title", "Post Content"])
            writer.writeheader()
            writer.writerows(scraped_data)
        print(f"Scraping complete. Data saved to {output_file}")
    else:
        print("Tidak ada thread yang berhasil di-scrape.")

# Masukan user input
if __name__ == "__main__":
    user = input("Masukkan username Kaskus : ").strip()
    iterations = int(input("Masukkan jumlah thread yang ingin di-scrape: ").strip())
    output_file = f"{user}_scrape_kaskus.csv"
    
    scrape_kaskus(user, iterations, output_file)
