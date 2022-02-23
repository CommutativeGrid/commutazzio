//console.log(chroma('#D4F880').darken().hex());

const length = 50; //length of the ladder
const multi = 20;
const Size = length * multi;
const pSize = 16; //point size
const z = "rgba(0, 0, 0, 0.3)",
    bl = "rgba(0, 0, 255, 0.5)",
    gr = "rgba(0, 255, 0, 0.5)",
    mg = "rgba(255, 0, 255, 0.5)",
    rd = "rgba(255, 0, 0, 0.5)";
const aq = "rgba(0, 255, 255, 0.5)",
    ye = "rgba(255, 255, 0, 0.5)";

function wake(I) {
    let K = I.split(",");
    return [`${K[0]},${K[1]},${length},-1`, `${length},-1,${K[2]},${K[3]}`];
    //return [K[0]+","+K[1]+",50,-1", "50,-1,"+K[2]+","+K[3]];
}

function linspace(start, stop, num, endpoint = true) {
    const div = endpoint ? (num - 1) : num;
    const step = (stop - start) / div;
    return Array.from({length: num}, (_, i) => start + step * i);
};

/*
points ?
*/
function maru(x) {
    return Math.max(0, Math.min(Math.round(x), 255));
};

function setCv(id) {
    const BASE = document.getElementById(id);
    const CV = document.createElement("canvas");
    CV.width = Size;
    CV.height = Size;
    CV.style.position = "absolute";
    CV.style.top = "10px";
    CV.style.left = "50px";
    CV.style.border = "#000000 2px solid";
    BASE.appendChild(CV);
    BASE.style.height = `${Size+20}px`;
    const CTX = CV.getContext("2d"); //controller for painting background grid lines and the diagonal line
    CTX.strokeStyle = z;
    CTX.lineWidth = 1;
    CTX.beginPath();
    CTX.moveTo(Size, 0);
    CTX.lineTo(0, Size);
    CTX.stroke();
    for (let i = 100; i < Size; i += 100) {
        //draw a grid line every 100px
        CTX.beginPath();
        CTX.moveTo(i, 0);
        CTX.lineTo(i, Size);
        CTX.stroke();
        CTX.beginPath();
        CTX.moveTo(0, i);
        CTX.lineTo(Size, i);
        CTX.stroke();
    }
    let max = 0,
        dim = 0,
        dotdec = {},
        Umax = 0,
        Dmax = 0;
    dotdec[`${length},-1,${length},-1`] = 0;
    for (let i = 0; i < length; i++) {
        for (let j = i; j < length; j++) {
            dotdec[`${i},${j},${length},-1`] = 0;
            dotdec[`${length},-1,${i},${j}`] = 0;
            //dotdec[i+","+j+",50,-1"]=0; dotdec["50,-1,"+i+","+j]=0;
        }
    }
    for (let I in dec) {
        let J = wake(I);
        dotdec[J[0]] += dec[I];
        dotdec[J[1]] += dec[I];
        if (
            J[0] != `${length},-1,${length},-1` &&
            J[1] != `${length},-1,${length},-1`
        ) {
            max = Math.max(max, dec[I]); //max for connecting lines
            // consider about changing this max.
            // may not appear in the final result.
        }
        //if(J[0]!="50,-1,50,-1"&&J[1]!="50,-1,50,-1"){ max=Math.max(max, dec[I]); }
    }
    for (let i = 0; i < length; i++) {
        for (let j = i; j < length; j++) {
            Dmax = Math.max(Dmax, dotdec[`${i},${j},${length},-1`]);
            Umax = Math.max(Umax, dotdec[`${length},-1,${i},${j}`]);
            // Dmax=Math.max(Dmax, dotdec[i+","+j+",50,-1"]);
            // Umax=Math.max(Umax, dotdec["50,-1,"+i+","+j]);
        }
    }
    const color = ["rgba(0, 0, 0, 0)"],
        colorD = ["rgba(0, 0, 0, 0)"], //up
        colorU = ["rgba(0, 0, 0, 0)"]; //down
    // https://gka.github.io/chroma.js/
    Cmax=Math.max(Dmax,Umax);
    //dot color bar part
    //color function
    colorMapDot = value => chroma.scale('RdYlBu')
        .domain([Cmax,0])(value);
    //bar values
    barValues=linspace(1,Cmax,200);
    colorBar=document.getElementById("colorBar");
    barValues.forEach(value=>{
        const bar=document.createElement("span");
        bar.style.backgroundColor=colorMapDot(value);
        bar.className="grad-step";
        colorBar.appendChild(bar);
    });
    startBar=document.createElement("span");
    startBar.className="grad-step";
    startBar.textContent="1";
    startBar.style.paddingRight="5px";
    endBar=document.createElement("span");
    endBar.className="grad-step";
    endBar.style.paddingLeft="5px";
    endBar.textContent=Cmax;
    colorBar.prepend(startBar);
    colorBar.append(endBar);
    // line color bar part
    //color function
    colorMapLine = value => chroma.scale('RdYlBu')
        .domain([max,0])(value);
    //line bar values
    lineBarValues=linspace(1,max,200);
    lineColorBar=document.getElementById("lineColorBar");
    lineBarValues.forEach(value=>{
        const bar=document.createElement("span");
        bar.style.backgroundColor= colorMapLine(value).alpha(0.5).css();
        bar.className="grad-step";
        lineColorBar.appendChild(bar);
    });
    startBar=document.createElement("span");
    startBar.className="grad-step";
    startBar.textContent="1";
    startBar.style.paddingRight="5px";
    endBar=document.createElement("span");
    endBar.className="grad-step";
    endBar.style.paddingLeft="5px";
    endBar.textContent=max;
    lineColorBar.prepend(startBar);
    lineColorBar.append(endBar);
    //colorD part, for dots in the lower area, not used for now
    for (let h = Dmax / 2, c = 255 / h, i = 0; i < Dmax; i++) {
        if (2 * i < Dmax) {
            colorD.push(
                "rgba(0, " + maru(c * i) + ", " + maru(255 - c * i) + ", 1)"
            );
        } else {
            colorD.push(
                "rgba(" +
                maru(c * (i - h)) +
                ", " +
                maru(255 - c * (i - h)) +
                ", 0, 1)"
            );
        }
    }
    //colorU part, for dots in the upper area, not used for now
    for (let h = Umax / 2, c = 255 / h, i = 0; i < Umax; i++) {
        if (2 * i < Umax) {
            colorU.push(
                "rgba(0, " + maru(c * i) + ", " + maru(255 - c * i) + ", 1)"
            );
        } else {
            colorU.push(
                "rgba(" +
                maru(c * (i - h)) +
                ", " +
                maru(255 - c * (i - h)) +
                ", 0, 1)"
            );
        }
    }
    //color part, for connecting lines
    for (let c = 255 / max, i = 0; i < max; i++) {
        color.push(
            "rgba(" + maru(c * i) + ", 0, " + maru(255 - c * i) + ", 0.2)"
        );
    }
    //plot connecting lines
    for (let I in dec) {
        if (dec[I] == 0) {
            continue;
        }
        let b1, d1, b2, d2, t1, l1, t2, l2;
        [b1, d1, b2, d2] = I.split(",").map((e) => multi * Number(e) + multi);
        if (d1 <= 0 || d2 <= 0 || (b1 == d1 && b2 == d2)) {
            continue;
        }
        let a = (d2 - b1) / (d1 - b2); //傾き、区間表現の条件から0≦a≦1が保証される
        CTX.strokeStyle = colorMapLine(dec[I]).alpha(0.5);
        //colorMapLine(value).alpha(0.5).css()
        //CTX.strokeStyle = color[dec[I]];
        CTX.lineWidth = 3;
        l1 = d1;
        t1 = Size - b1;
        l2 = b2;
        t2 = Size - d2; //dim+=((d1-b1)+(d2-b2))*dec[I]/10;
        if (a <= 1) {
            if (
                1 ||
                (0 <= b1 && b1 <= Size / 5 && (Size * 3) / 10 <= d1 && d1 <= Size)
            ) {
                //線を描画する条件
                CTX.beginPath();
                CTX.moveTo(l1, t1);
                CTX.lineTo(l2, t2);
                CTX.stroke();
                //console.log(dec[I])
            }
        }
    }
    //plot dots
    for (let i = 0; i < length; i++) {
        for (let j = i; j < length; j++) {
            let D = dotdec[`${i},${j},${length},-1`],
                U = dotdec[`${length},-1,${i},${j}`];
            //let D=dotdec[i+","+j+",50,-1"], U=dotdec["50,-1,"+i+","+j];
            if (D) {

                // CTX.fillRect(
                //   multi * j + multi - pSize / 2,
                //   Size - (multi * i + multi) - pSize / 2,
                //   pSize,
                //   pSize
                // ); //x,y,w,h
                // x,y is the corner. 1.5=3/2
                //CTX.fillRect((10*j+10)-1.5, (Size-(10*i+10))-1.5, 3, 3);
                var circle = new Path2D();
                circle.arc(multi * j + multi,
                    Size - (multi * i + multi),
                    pSize / 2, 0, 2 * Math.PI, false);//x,y,r,sAngle,eAngle,counterclockwise
                //CTX.fillStyle = colorD[D];
                CTX.fillStyle = colorMapDot(D);
                CTX.fill(circle);
                //CTX.lineWidth = 5;
                //CTX.strokeStyle = "#003300";
                //CTX.stroke();
            }
            if (U) {
                var circle = new Path2D();
                circle.arc(multi * i + multi,
                    Size - (multi * j + multi),
                    pSize / 2, 0, 2 * Math.PI, false);//x,y,r,sAngle,eAngle,counterclockwise
                CTX.fillStyle = colorMapDot(U);
                CTX.fill(circle);
                // CTX.fillStyle = colorU[U];
                // CTX.fillRect(
                //   multi * i + multi - pSize / 2,
                //   Size - (multi * j + multi) - pSize / 2,
                //   pSize,
                //   pSize
                // );
                //CTX.fillRect((10*i+10)-1.5, (Size-(10*j+10))-1.5, 3, 3);
            }
        }
    }
}