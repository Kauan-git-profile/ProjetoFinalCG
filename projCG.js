let faces;
let projectionMatrix;
let camZ;

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

  //em cada face
  for (let face of faces) {
    beginShape();

    //em cada vertice
    for (let vertx of face) {
      let tmp = [...vertx];
      tmp[2] += camZ; //translada o vertice para frente da camera
      let projVrtx = multiplyMatrixVector(projectionMatrix, tmp.concat(1.0)); //adiciona a componente w = 1 para cada vertice

      //normaliza o vertice projetado
      let x = projVrtx[0] / projVrtx[3];
      let y = projVrtx[1] / projVrtx[3];

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
