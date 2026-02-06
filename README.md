# ProjetoFinalCG
Projeto final de Computação gráfica, o objetivo é realizar todo o pipeline de modelagem de um objeto do mundo real para coordenadas de tela, além de realizar passos de preechimento de faces.


Fase 1: O Coração Matemático (O Universo)Antes de desenhar, você precisa de uma estrutura sólida de coordenadas.Padronizar o SRU: Defina o centro do seu cubo como $(0,0,0)$.Criar a Matriz $M_1$: Não use mais tmp[2] += camZ. Implemente a matriz de visualização real usando:VRP (Posição da câmera).P (Ponto focado).View Up (Vetor que aponta para cima).Gere os vetores $N, U, V$ e monte a matriz de mudança de base.Encapsular Matrizes: Crie uma função que multiplique matrizes $4 \times 4$ entre si (para concatenar $A \cdot B \cdot C \dots$).

Fase 2: O Pipeline de Geometria (Wireframe)Nesta fase, o objetivo é ver o objeto em "aramado", mas com a matemática correta.Projeção Normalizada: Aplique a matriz de projeção para levar os pontos para o intervalo $[-1, 1]$.Recorte 3D (Clipping): Implemente o algoritmo (como Sutherland-Hodgman) para os planos Near e Far. Se um vértice estiver fora, ele é "cortado" e novos vértices podem surgir.Mapeamento SRT ($M_2$): Transforme o intervalo $[-1, 1]$ para as coordenadas de tela $(0, 400)$.

Fase 3: Visibilidade e Sombreamento Constante (Flat)Aqui o objeto deixa de ser transparente.Back-face Culling: Para cada face, calcule o vetor normal ($\vec{n}$). Se o produto escalar entre $\vec{n}$ e o vetor de visão for $\le 0$, a face nem deve ser desenhada.Z-Buffer Inicial: Crie um array zBuffer do tamanho da tela (400x400) e preencha com "infinito".Rasterização Scanline: Escreva sua própria função de preencher triângulos (ou polígonos). Para cada pixel $(x, y)$, você deve calcular o $Z$ atual e comparar com o zBuffer.

Fase 4: Iluminação (Gouraud e Phong)A parte estética e técnica mais pesada.Cálculo de Normais Médias: Calcule a normal de cada vértice (média das normais das faces que o compartilham).Modelo de Reflexão: Implemente a fórmula de Phong (Ambiente + Difusa + Especular).Gouraud: Calcule a cor nos vértices e interpole a cor dentro da face.Phong (Sombreado): Interpole o vetor normal dentro da face e calcule a cor para cada pixel.

Fase 5: Interatividade e RefinamentoCâmera Móvel: Adicione controles de teclado para mover o VRP.Múltiplos Objetos: Garanta que o Z-Buffer funcione para dois objetos se cruzando.
