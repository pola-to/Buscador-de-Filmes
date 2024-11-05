import tkinter as tk
from tkinter import ttk
import requests
import random
from tkinter import messagebox
import webbrowser
from PIL import Image, ImageTk
from io import BytesIO
import threading
from googletrans import Translator

class MovieApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Finder")
        self.root.geometry("1000x800")
        self.root.configure(bg="#1a1a1a")
        
        self.api_key = "4a5c65e5aba428dd61cfbf586a3c401a"
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p/w500"  # Base URL para imagens
        self.headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI0YTVjNjVlNWFiYTQyOGRkNjFjZmJmNTg2YTNjNDAxYSIsInN1YiI6IjY3Mjk3MGU0MTRkNGEzOTk3MjAzNDFjNyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.llxUOjQgiAaylQd_1eE-T77aVXxqoThTYwVynop5R5Q"
        }

        # Inicializa o tradutor
        self.translator = Translator()
        
        self.create_widgets()
        self.load_genres()

    def create_widgets(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg="#1a1a1a")
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Título do app
        title_label = tk.Label(
            main_frame,
            text="🎬 Movie Finder",
            font=("Helvetica", 24, "bold"),
            bg="#1a1a1a",
            fg="white"
        )
        title_label.pack(pady=20)

        # Frame para seleção
        select_frame = tk.Frame(main_frame, bg="#1a1a1a")
        select_frame.pack(fill=tk.X, padx=50)

        genre_label = tk.Label(
            select_frame,
            text="Selecione o gênero:",
            font=("Helvetica", 12),
            bg="#1a1a1a",
            fg="white"
        )
        genre_label.pack(pady=5)

        self.genre_combo = ttk.Combobox(
            select_frame, 
            width=30, 
            font=("Helvetica", 12),
            state="readonly"  # Impede digitação manual
        )
        self.genre_combo.pack(pady=5)

        # Estilo da combobox
        style = ttk.Style()
        style.theme_use('default')
        style.configure(
            "TCombobox",
            fieldbackground="#2d2d2d",
            background="#2d2d2d",
            foreground="white",
            selectbackground="#4CAF50",
            selectforeground="white"
        )

        style.configure(
            "TProgressbar",
            thickness=10,
            troughcolor='#2d2d2d',
            background='#4CAF50',
            bordercolor='#1a1a1a',
            lightcolor='#4CAF50',
            darkcolor='#45a049'
        )

        # Salva referência ao botão de busca
        self.search_button = tk.Button(
            select_frame,
            text="Buscar Filme",
            command=self.find_movie,
            bg="#4CAF50",
            fg="white",
            font=("Helvetica", 12),
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.search_button.pack(pady=20)

        # Frame para informações do filme (inicialmente oculto)
        self.movie_frame = tk.Frame(main_frame, bg="#2d2d2d")
        
        # Frame para poster (esquerda)
        self.poster_frame = tk.Frame(self.movie_frame, bg="#2d2d2d")
        self.poster_frame.grid(row=0, column=0, padx=20, pady=20, sticky="n")

        # Label para o pôster do filme
        self.poster_label = tk.Label(self.poster_frame, bg="#2d2d2d")
        self.poster_label.pack()

        # Frame para informações (direita)
        self.info_frame = tk.Frame(self.movie_frame, bg="#2d2d2d")
        self.info_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # Labels para informações do filme
        self.title_var = tk.StringVar()
        self.rating_var = tk.StringVar()
        self.date_var = tk.StringVar()
        self.overview_var = tk.StringVar()

        # Título do filme
        self.title_label = tk.Label(
            self.info_frame,
            textvariable=self.title_var,
            font=("Helvetica", 20, "bold"),
            bg="#2d2d2d",
            fg="white",
            wraplength=500,
            justify=tk.LEFT
        )

        # Avaliação
        self.rating_label = tk.Label(
            self.info_frame,
            textvariable=self.rating_var,
            font=("Helvetica", 14),
            bg="#2d2d2d",
            fg="white"
        )

        # Data
        self.date_label = tk.Label(
            self.info_frame,
            textvariable=self.date_var,
            font=("Helvetica", 14),
            bg="#2d2d2d",
            fg="white"
        )

        # Sinopse título
        self.synopsis_title = tk.Label(
            self.info_frame,
            text="Sinopse:",
            font=("Helvetica", 14, "bold"),
            bg="#2d2d2d",
            fg="white"
        )

        # Sinopse conteúdo
        self.overview_label = tk.Label(
            self.info_frame,
            textvariable=self.overview_var,
            font=("Helvetica", 12),
            bg="#2d2d2d",
            fg="white",
            wraplength=500,
            justify=tk.LEFT
        )

        # Modifica a progressbar para modo determinado
        self.progress_frame = tk.Frame(main_frame, bg="#1a1a1a")
        self.progress_frame.pack(fill=tk.X, padx=50, pady=10)
        
        self.progress_label = tk.Label(
            self.progress_frame,
            text="Buscando filme...",
            font=("Helvetica", 10),
            bg="#1a1a1a",
            fg="white"
        )
        
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            mode='determinate',  # Modo determinado
            length=300,
            maximum=100
        )

    def load_poster(self, poster_path):
        if poster_path:
            try:
                response = requests.get(f"{self.image_base_url}{poster_path}")
                image = Image.open(BytesIO(response.content))
                
                # Redimensiona para um tamanho menor
                basewidth = 200  # Reduzido de 300 para 200
                wpercent = (basewidth/float(image.size[0]))
                hsize = int((float(image.size[1])*float(wpercent)))
                image = image.resize((basewidth, hsize), Image.Resampling.LANCZOS)
                
                photo = ImageTk.PhotoImage(image)
                self.poster_label.configure(image=photo)
                self.poster_label.image = photo
            except Exception as e:
                print(f"Erro ao carregar pôster: {e}")
        else:
            self.poster_label.configure(image="")
            self.poster_label.image = None

    def load_genres(self):
        url = f"{self.base_url}/genre/movie/list"
        params = {
            "api_key": self.api_key,
            "language": "pt-BR"  # Especifica o idioma português do Brasil
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            genres = response.json()["genres"]
            # Ordena os gêneros por nome
            genres = sorted(genres, key=lambda x: x["name"])
            self.genres = {genre["name"]: genre["id"] for genre in genres}
            
            # Define os valores da combobox
            self.genre_combo["values"] = list(self.genres.keys())
            self.genre_combo.set("Selecione um gênero")
            
            # Debug - imprime os gêneros para verificar
            print("Gêneros carregados:", self.genres)
        else:
            print(f"Erro ao carregar gêneros: {response.status_code}")
            print(response.text)

    def show_movie_info(self):
        # Mostra o frame do filme e todos os elementos
        self.movie_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        self.title_label.pack(anchor="w")
        self.rating_label.pack(anchor="w", pady=(10,0))
        self.date_label.pack(anchor="w", pady=(5,10))
        self.synopsis_title.pack(anchor="w")
        self.overview_label.pack(anchor="w", pady=(5,0))

    def translate_text(self, text):
        try:
            translated = self.translator.translate(text, dest='pt')
            return translated.text
        except:
            return text  # Retorna o texto original se a tradução falhar

    def show_loading(self):
        # Oculta o frame do filme se estiver visível
        if hasattr(self, 'movie_frame'):
            self.movie_frame.pack_forget()
        
        # Recria o frame da progress bar
        self.progress_frame.pack(fill=tk.X, padx=50, pady=10)
        self.progress_bar['value'] = 0
        self.progress_label.pack(pady=(0, 5))
        self.progress_bar.pack()
        self.root.update()

    def hide_loading(self):
        # Apenas esconde o frame da progress bar
        self.progress_frame.pack_forget()
        self.root.update()

    def update_progress(self, value, text):
        self.progress_bar['value'] = value
        self.progress_label['text'] = text
        self.root.update()

    def find_movie(self):
        # Desabilita o botão durante a busca
        self.search_button.config(state='disabled')
        
        selected_genre = self.genre_combo.get()
        if selected_genre == "Selecione um gênero":
            messagebox.showwarning("Aviso", "Por favor, selecione um gênero!")
            self.search_button.config(state='normal')
            return

        self.show_loading()
        self.update_progress(0, "Iniciando busca...")
        
        try:
            genre_id = self.genres[selected_genre]
            url = f"{self.base_url}/discover/movie"
            params = {
                "api_key": self.api_key,
                "with_genres": genre_id,
                "page": random.randint(1, 5),
                "language": "pt-BR"
            }
            
            self.update_progress(20, "Buscando filmes do gênero...")
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data["results"]:
                    self.update_progress(40, "Selecionando filme...")
                    movie = random.choice(data["results"])
                    
                    movie_details_url = f"{self.base_url}/movie/{movie['id']}"
                    details_params = {
                        "api_key": self.api_key,
                        "language": "en-US"
                    }
                    
                    self.update_progress(60, "Obtendo detalhes do filme...")
                    details_response = requests.get(movie_details_url, headers=self.headers, params=details_params)
                    
                    if details_response.status_code == 200:
                        details = details_response.json()
                        original_title = details['original_title']
                        rating = round(movie['vote_average'], 1)
                        
                        self.update_progress(80, "Carregando pôster...")
                        
                        try:
                            date_parts = movie['release_date'].split('-')
                            formatted_date = f"{date_parts[2]}/{date_parts[1]}/{date_parts[0]}"
                        except:
                            formatted_date = movie['release_date']
                        
                        overview = movie.get('overview', '').strip()
                        if not overview:
                            overview = "Não tem sinopse."
                        
                        # Carrega o pôster
                        if 'poster_path' in movie and movie['poster_path']:
                            response = requests.get(f"{self.image_base_url}{movie['poster_path']}")
                            if response.status_code == 200:
                                image = Image.open(BytesIO(response.content))
                                basewidth = 200
                                wpercent = (basewidth/float(image.size[0]))
                                hsize = int((float(image.size[1])*float(wpercent)))
                                image = image.resize((basewidth, hsize), Image.Resampling.LANCZOS)
                                photo = ImageTk.PhotoImage(image)
                        
                        self.update_progress(90, "Finalizando...")
                        
                        def update_ui():
                            self.update_progress(90, "Finalizando...")
                            
                            self.title_var.set(f"🎥 {original_title}")
                            self.rating_var.set(f"⭐ Nota: {rating}/10")
                            self.date_var.set(f"📅 Data de lançamento: {formatted_date}")
                            self.overview_var.set(overview)
                            
                            if 'photo' in locals():
                                self.poster_label.configure(image=photo)
                                self.poster_label.image = photo
                            else:
                                self.poster_label.configure(image="")
                                self.poster_label.image = None
                            
                            self.update_progress(100, "Concluído!")
                            
                            def finish_loading():
                                self.hide_loading()
                                self.show_movie_info()
                                # Reabilita o botão após concluir
                                self.search_button.config(state='normal')
                            
                            self.root.after(500, finish_loading)
                        
                        # Agenda a atualização da UI
                        self.root.after(100, update_ui)
                        
                    else:
                        self.hide_loading()
                        messagebox.showinfo("Info", "Erro ao obter detalhes do filme.")
                else:
                    self.hide_loading()
                    messagebox.showinfo("Info", "Nenhum filme encontrado para este gênero.")
            else:
                self.hide_loading()
                messagebox.showinfo("Info", "Erro ao buscar filmes.")
                
        except Exception as e:
            self.hide_loading()
            self.search_button.config(state='normal')  # Reabilita o botão em caso de erro
            messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")

def main():
    root = tk.Tk()
    app = MovieApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 