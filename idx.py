import zipfile
import os
import requests
import argparse
import json

def zip_folder(folder_path, output_path):
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)


def download_files(json_data, year, period,report_type, start, end):
    # Iterasi melalui hasil dan unduh setiap file dalam rentang yang ditentukan
    results = json_data['Results'][start:end]

    headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    for result in results:
        emiten_code = result['KodeEmiten']
        year = result['Report_Year']
        # period = result['Report_Period']
        attachments = result['Attachments']

        # Path untuk menyimpan file
        save_dir = os.path.join("download", str(year), period, report_type, emiten_code)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        for attachment in attachments:
            file_name = attachment['File_Name']

            file_path = attachment['File_Path']
            file_path = file_path.replace('//', '/')

            full_url = f"https://www.idx.co.id{file_path}"
            
            file_save_path = os.path.join(save_dir, file_name)
            
            # Cek jika file sudah ada
            if os.path.exists(file_save_path):
                print(f"{emiten_code} : File '{file_name}' sudah ada, tidak perlu diunduh ulang.")
                continue
            
            # Download file
            try:
                response = requests.get(full_url, headers=headers, allow_redirects=True, stream=True)
                response.raise_for_status()
                
                with open(file_save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"File {file_name} berhasil diunduh.")
            except requests.RequestException as e:
                print(f"Terjadi kesalahan saat mengunduh {full_url}: {e}")
        
            # file_response = requests.get(full_url, headers=headers)
            # if file_response.status_code == 200:
            #     with open(file_save_path, "wb") as file:
            #         file.write(file_response.content)
            #     print(f"{emiten_code} : File '{file_name}' berhasil diunduh dan disimpan di '{file_save_path}'")
            # else:
            #     print(f"{emiten_code} : Gagal mengunduh file '{file_name}' dari '{full_url}'")

def get_json_data(year, period, report_type):
    json_path = f"json/{year}_{period}_{report_type}.json"
    
    # Jika file JSON sudah ada, baca dari file
    if os.path.exists(json_path):
        with open(json_path, 'r') as json_file:
            json_data = json.load(json_file)
            print(f"Membaca data JSON dari '{json_path}'")
    else:
        # URL untuk mendapatkan JSON data
        # url = f"https://www.idx.co.id/primary/ListedCompany/GetFinancialReport?indexFrom=1&pageSize=12&year={year}&reportType={report_type}&EmitenType=s&period={period}&kodeEmiten=&SortColumn=KodeEmiten&SortOrder=asc"
        url = f"https://www.idx.co.id/primary/ListedCompany/GetFinancialReport?indexFrom=1&pageSize=1000&year={year}&reportType={report_type}&EmitenType=s&periode={period}&kodeEmiten=&SortColumn=KodeEmiten&SortOrder=asc"

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
            "cross-origin-resource-policy":"cross-origin",

        }

        # Mengambil data JSON dari URL
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            json_data = response.json()
            # Simpan JSON ke file
            save_path = "json"
            if not os.path.exists(save_path):
                os.makedirs(save_path)

            file_name = f"{year}_{period}_{report_type}.json"
            file_path = os.path.join(save_path, file_name)
            
            with open(file_path, 'w') as json_file:
                json.dump(json_data, json_file, indent=4)
            
            print(f"Response JSON berhasil disimpan di '{file_path}'")
        else:
            print(response)
            print("Gagal mendapatkan data JSON dari URL.")
            exit()

    return json_data

def count_folders(path):
    try:
        # Mendapatkan daftar isi folder
        entries = os.listdir(path)
        # Menghitung jumlah folder
        folder_count = sum(1 for entry in entries if os.path.isdir(os.path.join(path, entry)))
        return folder_count
    except FileNotFoundError:
        print("Folder tidak ditemukan")
        return 0
    except PermissionError:
        print("Tidak memiliki izin untuk mengakses folder")
        return 0
    
def main(year, period, report_type, start, end, is_zip=0):
    # Ambil data JSON
    json_data = get_json_data(year, period, report_type)

    # Unduh file berdasarkan data JSON
    download_files(json_data, year, period,report_type, start, end)

    # zip_folder();
    save_dir = os.path.join("download", str(year), period, report_type)
    


    # print(is_zip)
    jml_folder = count_folders(save_dir)
    print(f"Jumlah Folder : {jml_folder}")
    
    if (is_zip == 1):
        output_path = os.path.join("download", str(year), period, report_type) + '.zip'
        
        print(save_dir)
        print(output_path)

        zip_folder(save_dir, output_path)

    
    

# zip_folder(folder_path, output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download files based on year and period.')
    parser.add_argument('year', type=int, help='Year of the report')
    parser.add_argument('period', type=str, help='Period of the report')
    parser.add_argument('report_type', type=str, help='Type of the report')
    parser.add_argument('start', type=int, help='Start index for the results to download')
    parser.add_argument('end', type=int, help='End index for the results to download')
    parser.add_argument('is_zip', type=int, help='Is Zip index for the results to download')
    
    args = parser.parse_args()

    if (args.is_zip):
        main(args.year, args.period,args.report_type, args.start, args.end, args.is_zip)
    else:
        main(args.year, args.period,args.report_type, args.start, args.end)
        
