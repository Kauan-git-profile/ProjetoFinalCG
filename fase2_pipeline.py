"""
1. Aplicação da matriz de normalização M1
2. Projeção Perspectiva (matriz P)
3. Recorte 3D (Clipping)
4. Normalização (divisão homogênea)
5. Mapeamento SRT para coordenadas de tela (matriz M2)
"""

import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass
from enum import IntFlag

# ============================================================================
# ESTRUTURAS DE DADOS
# ============================================================================

@dataclass
class Ponto4D:
    """Ponto em coordenadas homogêneas (x, y, z, h)"""
    x: float
    y: float
    z: float
    h: float = 1.0
    
    def to_array(self) -> np.ndarray:
        """Converte para array NumPy"""
        return np.array([self.x, self.y, self.z, self.h])
    
    @classmethod
    def from_array(cls, arr: np.ndarray) -> 'Ponto4D':
        """Cria Ponto4D a partir de array NumPy"""
        return cls(arr[0], arr[1], arr[2], arr[3])
    
    def __repr__(self):
        return f"Ponto4D({self.x:.3f}, {self.y:.3f}, {self.z:.3f}, {self.h:.3f})"


@dataclass
class PontoTela:
    """Ponto em coordenadas de tela"""
    x: int
    y: int
    z: float  # Profundidade para Z-buffer
    
    def __repr__(self):
        return f"PontoTela({self.x}, {self.y}, z={self.z:.3f})"


@dataclass
class Cubo:
    """Cubo com 8 vértices e 12 arestas"""
    vertices: List[Ponto4D]  # 8 vértices
    arestas: List[Tuple[int, int]]  # 12 arestas (índices)
    
    @classmethod
    def criar_cubo_unitario(cls, centro: Tuple[float, float, float] = (0, 0, 0),
                           tamanho: float = 1.0) -> 'Cubo':
        """Cria cubo centrado com tamanho especificado"""
        cx, cy, cz = centro
        s = tamanho / 2.0
        
        vertices = [
            Ponto4D(cx - s, cy - s, cz - s, 1.0),  # frente baixo esquerdo
            Ponto4D(cx + s, cy - s, cz - s, 1.0),  # frente baixo direito
            Ponto4D(cx + s, cy + s, cz - s, 1.0),  # frente cima direito
            Ponto4D(cx - s, cy + s, cz - s, 1.0),  # frente cima esquerdo
            Ponto4D(cx - s, cy - s, cz + s, 1.0),  # trás baixo esquerdo
            Ponto4D(cx + s, cy - s, cz + s, 1.0),  # trás baixo direito
            Ponto4D(cx + s, cy + s, cz + s, 1.0),  # trás cima direito
            Ponto4D(cx - s, cy + s, cz + s, 1.0),  # trás cima esquerdo
        ]
        
        arestas = [
            (0, 1), (1, 2), (2, 3), (3, 0),  # Face frontal
            (4, 5), (5, 6), (6, 7), (7, 4),  # Face traseira
            (0, 4), (1, 5), (2, 6), (3, 7),  # Arestas conectando
        ]
        
        return cls(vertices, arestas)


# ============================================================================
# OPERAÇÕES COM MATRIZES
# ============================================================================

def multiplica_matriz_ponto(matriz: np.ndarray, ponto: Ponto4D) -> Ponto4D:
    """
    Multiplica matriz 4x4 por ponto homogêneo
    
    Args:
        matriz: Matriz 4x4 (NumPy array)
        ponto: Ponto em coordenadas homogêneas
        
    Returns:
        Ponto transformado
    """
    p_array = ponto.to_array()
    resultado_array = matriz @ p_array
    return Ponto4D.from_array(resultado_array)


def imprime_matriz(nome: str, matriz: np.ndarray):
    """Imprime matriz formatada"""
    print(f"\n{nome}:")
    print(matriz)


# ============================================================================
# MATRIZ DE PROJEÇÃO PERSPECTIVA (P)
# ============================================================================

def cria_projecao_perspectiva(near: float, far: float) -> np.ndarray:
    """
    Cria matriz de projeção perspectiva P
    
    Esta matriz assume que em coordenadas de câmera:
    - Z positivo aponta PARA DENTRO da cena (convenção OpenGL)
    - Objetos visíveis têm Z positivo
    
    Args:
        near: Distância do plano near (próximo)
        far: Distância do plano far (distante)
        
    Returns:
        Matriz 4x4 de projeção perspectiva
    """
    P = np.zeros((4, 4))
    
    P[0, 0] = 1.0
    P[1, 1] = 1.0
    P[2, 2] = far / (far - near)
    P[2, 3] = -1.0
    P[3, 2] = (far * near) / (far - near)
    P[3, 3] = 0.0
    
    return P


def cria_projecao_perspectiva_z_negativo(near: float, far: float) -> np.ndarray:
    """
    Matriz de projeção para sistema com Z negativo
    
    Args:
        near: Distância do plano near (valor positivo)
        far: Distância do plano far (valor positivo)
        
    Returns:
        Matriz 4x4 de projeção perspectiva
    """
    P = np.zeros((4, 4))
    
    P[0, 0] = 1.0
    P[1, 1] = 1.0
    P[2, 2] = -(far + near) / (far - near)
    P[2, 3] = 1.0  # Positivo para Z negativo!
    P[3, 2] = -(2.0 * far * near) / (far - near)
    P[3, 3] = 0.0
    
    return P


# ============================================================================
# NORMALIZAÇÃO HOMOGÊNEA
# ============================================================================

def normaliza_homogenea(ponto: Ponto4D, epsilon: float = 1e-10) -> Ponto4D:
    """
    Divide coordenadas homogêneas para obter NDC
    
    Após esta operação:
    -1 <= x <= 1
    -1 <= y <= 1
     0 <= z <= 1
    
    Args:
        ponto: Ponto em coordenadas homogêneas
        epsilon: Tolerância para divisão por zero
        
    Returns:
        Ponto normalizado (NDC)
    """
    if abs(ponto.h) < epsilon:
        print("AVISO: Divisão por h muito pequeno!")
        return Ponto4D(0.0, 0.0, 0.0, 1.0)
    
    return Ponto4D(
        ponto.x / ponto.h,
        ponto.y / ponto.h,
        ponto.z / ponto.h,
        1.0
    )


# ============================================================================
# RECORTE 3D (CLIPPING)
# ============================================================================

class CodigoRecorte(IntFlag):
    """Códigos de região para Cohen-Sutherland"""
    INSIDE = 0
    LEFT = 1
    RIGHT = 2
    BOTTOM = 4
    TOP = 8
    NEAR = 16
    FAR = 32


def calcula_codigo_regiao(ponto: Ponto4D, epsilon: float = 1e-10) -> CodigoRecorte:
    """
    Calcula código de região para ponto em coordenadas homogêneas
    
    Em coordenadas homogêneas, os limites do volume de visualização são:
    -h <= x <= h
    -h <= y <= h
     0 <= z <= h
    
    Args:
        ponto: Ponto em coordenadas homogêneas
        epsilon: Tolerância numérica
        
    Returns:
        Código de região
    """
    codigo = CodigoRecorte.INSIDE
    
    # Se h é muito pequeno, considerar fora
    if abs(ponto.h) < epsilon:
        return CodigoRecorte.LEFT | CodigoRecorte.RIGHT | CodigoRecorte.BOTTOM | \
               CodigoRecorte.TOP | CodigoRecorte.NEAR | CodigoRecorte.FAR
    
    # Se h é negativo, ponto está atrás da câmera
    if ponto.h < 0:
        codigo |= CodigoRecorte.NEAR
    
    h_abs = abs(ponto.h)
    
    if ponto.x < -h_abs:
        codigo |= CodigoRecorte.LEFT
    if ponto.x > h_abs:
        codigo |= CodigoRecorte.RIGHT
    if ponto.y < -h_abs:
        codigo |= CodigoRecorte.BOTTOM
    if ponto.y > h_abs:
        codigo |= CodigoRecorte.TOP
    if ponto.z < 0:
        codigo |= CodigoRecorte.NEAR
    if ponto.z > h_abs:
        codigo |= CodigoRecorte.FAR
    
    return codigo


def ponto_visivel(ponto: Ponto4D, epsilon: float = 1e-10) -> bool:
    """
    Verifica se ponto está dentro do volume de visualização
    
    Args:
        ponto: Ponto em coordenadas homogêneas (após projeção)
        epsilon: Tolerância numérica
        
    Returns:
        True se ponto visível
    """
    return calcula_codigo_regiao(ponto, epsilon) == CodigoRecorte.INSIDE


def interpola_pontos(p1: Ponto4D, p2: Ponto4D, t: float) -> Ponto4D:
    """
    Interpola linearmente entre dois pontos
    
    Args:
        p1: Primeiro ponto
        p2: Segundo ponto
        t: Parâmetro de interpolação [0, 1]
        
    Returns:
        Ponto interpolado
    """
    return Ponto4D(
        p1.x + t * (p2.x - p1.x),
        p1.y + t * (p2.y - p1.y),
        p1.z + t * (p2.z - p1.z),
        p1.h + t * (p2.h - p1.h)
    )


def intersecao_com_plano(p1: Ponto4D, p2: Ponto4D, 
                         plano: CodigoRecorte) -> Ponto4D:
    """
    Encontra interseção de linha com plano em coordenadas homogêneas
    
    Args:
        p1: Primeiro ponto
        p2: Segundo ponto
        plano: Plano de recorte
        
    Returns:
        Ponto de interseção
    """
    epsilon = 1e-10
    
    if plano == CodigoRecorte.LEFT:
        num = -(p1.x + p1.h)
        den = (p2.x + p2.h) - (p1.x + p1.h)
    elif plano == CodigoRecorte.RIGHT:
        num = -(p1.x - p1.h)
        den = (p2.x - p2.h) - (p1.x - p1.h)
    elif plano == CodigoRecorte.BOTTOM:
        num = -(p1.y + p1.h)
        den = (p2.y + p2.h) - (p1.y + p1.h)
    elif plano == CodigoRecorte.TOP:
        num = -(p1.y - p1.h)
        den = (p2.y - p2.h) - (p1.y - p1.h)
    elif plano == CodigoRecorte.NEAR:
        num = -p1.z
        den = p2.z - p1.z
    elif plano == CodigoRecorte.FAR:
        num = -(p1.z - p1.h)
        den = (p2.z - p2.h) - (p1.z - p1.h)
    else:
        return p1
    
    # Evita divisão por zero
    if abs(den) < epsilon:
        return p1
    
    t = num / den
    t = max(0.0, min(1.0, t))  # Clamp entre 0 e 1
    
    return interpola_pontos(p1, p2, t)


def recorta_linha_3d(p1: Ponto4D, p2: Ponto4D) -> Optional[Tuple[Ponto4D, Ponto4D]]:
    """
    Recorta linha no volume de visualização 3D usando Cohen-Sutherland
    
    Args:
        p1: Primeiro ponto da linha (em coord. homogêneas após projeção)
        p2: Segundo ponto da linha
        
    Returns:
        Tupla (p1_recortado, p2_recortado) se linha visível, None caso contrário
    """
    MAX_ITERACOES = 10
    
    for _ in range(MAX_ITERACOES):
        c1 = calcula_codigo_regiao(p1)
        c2 = calcula_codigo_regiao(p2)
        
        # Ambos dentro
        if (c1 | c2) == CodigoRecorte.INSIDE:
            return (p1, p2)
        
        # Ambos fora do mesmo lado
        if (c1 & c2) != 0:
            return None
        
        # Linha cruza o volume - recortar
        # Escolhe ponto fora
        codigo_fora = c1 if c1 != CodigoRecorte.INSIDE else c2
        
        # Encontra interseção com o plano apropriado
        if codigo_fora & CodigoRecorte.LEFT:
            p_inter = intersecao_com_plano(p1, p2, CodigoRecorte.LEFT)
        elif codigo_fora & CodigoRecorte.RIGHT:
            p_inter = intersecao_com_plano(p1, p2, CodigoRecorte.RIGHT)
        elif codigo_fora & CodigoRecorte.BOTTOM:
            p_inter = intersecao_com_plano(p1, p2, CodigoRecorte.BOTTOM)
        elif codigo_fora & CodigoRecorte.TOP:
            p_inter = intersecao_com_plano(p1, p2, CodigoRecorte.TOP)
        elif codigo_fora & CodigoRecorte.NEAR:
            p_inter = intersecao_com_plano(p1, p2, CodigoRecorte.NEAR)
        elif codigo_fora & CodigoRecorte.FAR:
            p_inter = intersecao_com_plano(p1, p2, CodigoRecorte.FAR)
        else:
            break
        
        # Substitui ponto fora pela interseção
        if codigo_fora == c1:
            p1 = p_inter
        else:
            p2 = p_inter
    
    return None  # Não convergiu


# ============================================================================
# MAPEAMENTO SRT (SCALE, ROTATE, TRANSLATE) - MATRIZ M2
# ============================================================================

def cria_matriz_srt(xmin: float, xmax: float, 
                    ymin: float, ymax: float,
                    zmin: float = 0.0, zmax: float = 1.0) -> np.ndarray:
    """
    Cria matriz de mapeamento de NDC para coordenadas de tela
    
    NDC: x,y em [-1, 1] e z em [0, 1]
    Tela: x em [xmin, xmax], y em [ymin, ymax], z em [zmin, zmax]
    
    Args:
        xmin, xmax: Limites X da tela
        ymin, ymax: Limites Y da tela
        zmin, zmax: Limites Z (profundidade)
        
    Returns:
        Matriz 4x4 de mapeamento SRT
    """
    M2 = np.zeros((4, 4))
    
    # Escala
    M2[0, 0] = (xmax - xmin) / 2.0
    M2[1, 1] = (ymax - ymin) / 2.0
    M2[2, 2] = (zmax - zmin)
    
    # Translação
    M2[3, 0] = (xmax + xmin) / 2.0
    M2[3, 1] = (ymax + ymin) / 2.0
    M2[3, 2] = zmin
    M2[3, 3] = 1.0
    
    return M2


def cria_matriz_srt_raster(xmin: float, xmax: float,
                           ymin: float, ymax: float,
                           zmin: float = 0.0, zmax: float = 1.0) -> np.ndarray:
    """
    Matriz SRT para displays raster (Y invertido)
    
    Em displays raster, Y cresce para baixo
    
    Args:
        xmin, xmax: Limites X da tela
        ymin, ymax: Limites Y da tela
        zmin, zmax: Limites Z (profundidade)
        
    Returns:
        Matriz 4x4 de mapeamento SRT com Y invertido
    """
    M2 = np.zeros((4, 4))
    
    # Escala (Y negativo para inverter)
    M2[0, 0] = (xmax - xmin) / 2.0
    M2[1, 1] = -(ymax - ymin) / 2.0  # Invertido!
    M2[2, 2] = (zmax - zmin)
    
    # Translação
    M2[3, 0] = (xmax + xmin) / 2.0
    M2[3, 1] = (ymax + ymin) / 2.0
    M2[3, 2] = zmin
    M2[3, 3] = 1.0
    
    return M2


# ============================================================================
# PIPELINE COMPLETO
# ============================================================================

class PipelineGrafico:
    
    def __init__(self, near: float, far: float, 
                 largura_tela: int, altura_tela: int,
                 usa_z_negativo: bool = True):
        """
        Args:
            near: Distância do plano near
            far: Distância do plano far
            largura_tela: Largura da tela em pixels
            altura_tela: Altura da tela em pixels
            usa_z_negativo: True se Z negativo = frente da câmera
        """
        self.near = near
        self.far = far
        self.largura = largura_tela
        self.altura = altura_tela
        
        # Cria matrizes
        if usa_z_negativo:
            self.P = cria_projecao_perspectiva_z_negativo(near, far)
        else:
            self.P = cria_projecao_perspectiva(near, far)
        
        self.M2 = cria_matriz_srt_raster(
            0, largura_tela, 
            0, altura_tela,
            0, 1
        )
    
    def processa_ponto(self, p_camera: Ponto4D, 
                       verbose: bool = False) -> Optional[PontoTela]:
        """
        Aplica pipeline em um ponto
        
        Args:
            p_camera: Ponto em coordenadas de câmera (após M1)
            verbose: Se True, imprime passos
            
        Returns:
            PontoTela ou None se ponto invisível
        """
        if verbose:
            print(f"\n--- Pipeline para {p_camera} ---")
        
        # 1. Projeção perspectiva
        p_proj = multiplica_matriz_ponto(self.P, p_camera)
        if verbose:
            print(f"  Após projeção: {p_proj}")
        
        # 2. Verificar visibilidade
        if not ponto_visivel(p_proj):
            if verbose:
                print("  Ponto invisível!")
            return None
        
        # 3. Normalização homogênea
        p_ndc = normaliza_homogenea(p_proj)
        if verbose:
            print(f"  NDC: {p_ndc}")
        
        # 4. Mapeamento para tela
        p_tela_temp = multiplica_matriz_ponto(self.M2, p_ndc)
        if verbose:
            print(f"  Tela: {p_tela_temp}")
        
        # 5. Converte para inteiros
        return PontoTela(
            int(p_tela_temp.x + 0.5),
            int(p_tela_temp.y + 0.5),
            p_tela_temp.z
        )
    
    def processa_linha(self, p1_cam: Ponto4D, p2_cam: Ponto4D,
                      verbose: bool = False) -> Optional[Tuple[PontoTela, PontoTela]]:
        """
        Processa uma aresta
        
        Args:
            p1_cam: Primeiro ponto em coord. câmera
            p2_cam: Segundo ponto em coord. câmera
            verbose: Se True, imprime passos
            
        Returns:
            Tupla (PontoTela1, PontoTela2) ou None se linha invisível
        """
        # Projeção
        p1_proj = multiplica_matriz_ponto(self.P, p1_cam)
        p2_proj = multiplica_matriz_ponto(self.P, p2_cam)
        
        # Recorte 3D
        resultado = recorta_linha_3d(p1_proj, p2_proj)
        if resultado is None:
            if verbose:
                print("Linha invisível (recortada)")
            return None
        
        p1_rec, p2_rec = resultado
        
        # NDC
        p1_ndc = normaliza_homogenea(p1_rec)
        p2_ndc = normaliza_homogenea(p2_rec)
        
        # Tela
        p1_tela_temp = multiplica_matriz_ponto(self.M2, p1_ndc)
        p2_tela_temp = multiplica_matriz_ponto(self.M2, p2_ndc)
        
        pt1 = PontoTela(
            int(p1_tela_temp.x + 0.5),
            int(p1_tela_temp.y + 0.5),
            p1_tela_temp.z
        )
        
        pt2 = PontoTela(
            int(p2_tela_temp.x + 0.5),
            int(p2_tela_temp.y + 0.5),
            p2_tela_temp.z
        )
        
        return (pt1, pt2)
    
    def processa_cubo(self, cubo: Cubo, M1: np.ndarray,
                     verbose: bool = False) -> List[Tuple[PontoTela, PontoTela]]:
        """
        Processa todas as arestas de um cubo
        
        Args:
            cubo: Cubo a processar
            M1: Matriz de visualização (Fase 1)
            verbose: Se True, imprime informações
            
        Returns:
            Lista de linhas visíveis (tuplas de PontoTela)
        """
        linhas_visiveis = []
        
        # 1. Transforma todos vértices por M1
        vertices_cam = []
        for v in cubo.vertices:
            v_cam = multiplica_matriz_ponto(M1, v)
            vertices_cam.append(v_cam)
        
        # 2. Processa cada aresta
        for i, (idx1, idx2) in enumerate(cubo.arestas):
            if verbose:
                print(f"\nAresta {i}: {idx1} -> {idx2}")
            
            resultado = self.processa_linha(
                vertices_cam[idx1],
                vertices_cam[idx2],
                verbose
            )
            
            if resultado is not None:
                linhas_visiveis.append(resultado)
                if verbose:
                    pt1, pt2 = resultado
                    print(f"  Visível: {pt1} -> {pt2}")
        
        return linhas_visiveis


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def cria_matriz_identidade() -> np.ndarray:
    """Cria matriz identidade 4x4"""
    return np.eye(4)


def cria_matriz_translacao(tx: float, ty: float, tz: float) -> np.ndarray:
    """Cria matriz de translação"""
    T = np.eye(4)
    T[3, 0] = tx
    T[3, 1] = ty
    T[3, 2] = tz
    return T


def cria_matriz_escala(sx: float, sy: float, sz: float) -> np.ndarray:
    """Cria matriz de escala"""
    S = np.eye(4)
    S[0, 0] = sx
    S[1, 1] = sy
    S[2, 2] = sz
    return S


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("FASE 2: PIPELINE DE GEOMETRIA - Python")
    print("=" * 60)
    
    # Configuração
    near = 1.0
    far = 10.0
    largura = 800
    altura = 600
    
    # Cria pipeline
    pipeline = PipelineGrafico(near, far, largura, altura, usa_z_negativo=True)
    
    print("\n--- Teste 1: Ponto no eixo Z ---")
    p_teste = Ponto4D(0, 0, -5, 1)  # 5 unidades na frente
    resultado = pipeline.processa_ponto(p_teste, verbose=True)
    if resultado:
        print(f"Resultado final: {resultado}")
        print(f"Esperado: próximo de ({largura//2}, {altura//2})")
    
    print("\n--- Teste 2: Cubo ---")
    # Cria cubo centrado em (0, 0, -5)
    cubo = Cubo.criar_cubo_unitario(centro=(0, 0, -5), tamanho=2)
    
    # Matriz M1 simples (identidade - cubo já está em coord. câmera)
    M1 = cria_matriz_identidade()
    
    linhas = pipeline.processa_cubo(cubo, M1, verbose=False)
    print(f"\nTotal de arestas visíveis: {len(linhas)}")
    for i, (pt1, pt2) in enumerate(linhas):
        print(f"  Aresta {i}: {pt1} -> {pt2}")
