let faces;
let projectionMatrix;
let camZ;

//PARÂMTROS DA CAMERA

let camera = {
  VRP: [0, 0, 0], //View Reference Point
  P: [100, 150, 400], //Position
  viewup: [0, 1, 0], //View Up Vector

  //Parâmetros do volume de visão

  SU: 200,
  SV: 200,
  dp: 600,
  near: 1,
  far: 1000,
}

function setup() {
  createCanvas(400, 400);

  //Estrutura de dados do Cubo

  //Criando os vértices do cubo
  let vertices = [];

  vertices.push([-50.0, -50.0, 50.0]);
  vertices.push([50.0, -50.0, 50.0]);
  vertices.push([50.0, 50.0, 50.0]);
  vertices.push([-50.0, 50.0, 50.0]);

  vertices.push([-50.0, -50.0, -50.0]);
  vertices.push([50.0, -50.0, -50.0]);
  vertices.push([50.0, 50.0, -50.0]);
  vertices.push([-50.0, 50.0, -50.0]);

  //Criando as faces do cubo

  faces = [];

  faces.push([vertices[0], vertices[1], vertices[2], vertices[3]]); // Frente
  faces.push([vertices[4], vertices[5], vertices[6], vertices[7]]); // Atrás
  faces.push([vertices[4], vertices[5], vertices[1], vertices[0]]); // Superior
  faces.push([vertices[3], vertices[2], vertices[6], vertices[7]]); // Inferior
  faces.push([vertices[4], vertices[0], vertices[3], vertices[7]]); // Esquerda
  faces.push([vertices[1], vertices[5], vertices[6], vertices[2]]); // Direita

  projectionMatrix = [];
  projectionMatrix.push([1.0, 0.0, 0.0, 0.0]);
  projectionMatrix.push([0.0, 1.0, 0.0, 0.0]);
  projectionMatrix.push([0.0, 0.0, 1.0, 0.0]);
  projectionMatrix.push([0.0, 0.0, 0.0, 1.0]);

  //calcular o FOV o angulo que determina o quanto do mundo 3D é visto na tela 2D
  let fov = 1.0 / tan(PI / 6.0); //30 graus
  let ar = width / height; //aspect ratio

  //planos near e far
  camZ = 350;
  let near = camZ / 10.0;
  let far = camZ * 10.0;

  //definindo a matriz de projeção perspectiva
  projectionMatrix[0][0] = ar * fov;
  projectionMatrix[1][1] = fov;
  projectionMatrix[2][2] = -(far + near) / (far - near);
  projectionMatrix[2][3] = (-2.0 * (far * near)) / (far - near);
  projectionMatrix[3][2] = 1.0;
  projectionMatrix[3][3] = 0.0;

  /* face[0][0].concat([1]); //adiciona a componente w = 1 para cada vertice
  face[0][1].concat([1]);
  face[0][2].concat([1]);
  face[0][3].concat([1]);*/
}

function draw() {
  background(220);
  noFill(); // Para ver através do cubo
  stroke(0); // Linhas pretas

  let viewMatrix = createViewMatrix();
  let viewProjectionMatrix = multiplyMatrices(projectionMatrix, viewMatrix);

  //em cada face
  for (let face of faces) {
    beginShape();

    //em cada vertice
    for (let vertx of face) {
      
      //VÉRTICE NO sru
      let vertex4D = [...vertx, 1.0]; // [x, y, z, 1]

      //Aplicar transformação view mais projeção
      let projVrtx = multiplyMatrixVector(viewProjectionMatrix, vertex4D);

      //normaliza o vertice projetado
      let w = projVrtx[3];
      let x = projVrtx[0] / w;
      let y = projVrtx[1] / w;
      let z = projVrtx[2] / w;

      //mudança de sistema de coordenadas (origem no centro da tela)
      x = (x + 1) * 0.5 * width;
      y = (1 - (y + 1) * 0.5) * height;

      vertex(x, y);
    }

    endShape(CLOSE);
  }
}

//multiplica uma matriz 4x4 por um vetor 4D

//multiplica os vertices pela matriz de projeção, sai do 3d para o 2d
function multiplyMatrixVector(matrix, vector) {
  let result = [0, 0, 0, 0];

  for (let i = 0; i < 4; i++) {
    result[i] =
      vector[0] * matrix[i][0] +
      vector[1] * matrix[i][1] +
      vector[2] * matrix[i][2] +
      vector[3] * matrix[i][3];
  }

  return result;
}

function multiplyMatrices(a, b) {
    let result = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ];
    
    for (let i = 0; i < 4; i++) {
        for (let j = 0; j < 4; j++) {
            for (let k = 0; k < 4; k++) {
                result[i][j] += a[i][k] * b[k][j];
            }
        }
    }
    
    return result;
}
/*A View Matrix (matriz de visão) é a
matriz que transforma o mundo para o 
sistema de coordenadas da câmera.
Alterar ela muda posição e orientação da câmera,
sem precisar mover os objetos.*/ 
function createViewMatrix() {
  
  
  // Matriz de View: transforma do SRU para o SRD (Sistema de Referência da Câmera)

  // Definindo os vetores da câmera U, V, N
  let n = normalize(subtractVectors(camera.P, camera.VRP));  // Vetor N (para frente)
  let u = normalize(crossProduct(camera.viewup, n));         // Vetor U (para direita)
  let v = crossProduct(n, u);  // Vetor V (para cima)

  // Criando a matriz de rotação
  let rotationMatrix = [
    [u[0], u[1], u[2], 0],
    [v[0], v[1], v[2], 0],
    [n[0], n[1], n[2], 0],
    [0,    0,    0,    1]
  ];

  // Criando a matriz de translação, deve levar a câmera para a origem
  let translationMatrix = [
    [1, 0, 0, -camera.P[0]],
    [0, 1, 0, -camera.P[1]],
    [0, 0, 1, -camera.P[2]],
    [0, 0, 0, 1]
  ];

  //Matriz de view

  return multiplyMatrices(rotationMatrix, translationMatrix);

}


function subtractVectors(a, b) {
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
}

function normalize(v) {
    let length = Math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2]);
    return [v[0]/length, v[1]/length, v[2]/length];
}

function crossProduct(a, b) {
    return [
        a[1]*b[2] - a[2]*b[1],
        a[2]*b[0] - a[0]*b[2],
        a[0]*b[1] - a[1]*b[0]
    ];
}
